"""特殊表格识别与 HTML / Markdown 渲染。"""

from __future__ import annotations

import html
import re

from bs4 import NavigableString, Tag

from inline import inline_children, inline_table_cell

TABLE_KIND_CLASSES = {
    "kana-stroke": "jp-kana-table jp-kana-stroke",
    "kana-clip": "jp-kana-table jp-kana-clip",
    "kana-flip": "jp-kana-table jp-kana-flip",
    "practice": "jp-practice-table",
    "practice-grid": "jp-practice-table jp-practice-grid",
    "grammar": "jp-grammar-table",
    "layout": "jp-layout-table",
    "li-answer": "jp-answer-table",
}


def wrap_kana_reading_spans(content: str) -> str:
    """将罗马音注记包成 <span class="jp-kana-reading">。"""
    content = re.sub(
        r"<span>\(([^)]+)\)</span>",
        r'<span class="jp-kana-reading">(\1)</span>',
        content,
    )
    content = re.sub(
        r"(<br\s*/?>\s*)\(([^)]+)\)(?!\s*</span>)",
        r'\1<span class="jp-kana-reading">(\2)</span>',
        content,
        flags=re.I,
    )
    return content


def table_has_border_style(table: Tag) -> bool:
    if table.get("border"):
        return True
    style = table.get("style") or ""
    return bool(re.search(r"border\s*[:：]", style, re.I))


def is_li_nested_table(table: Tag) -> bool:
    """列表项内嵌的答案小表（如 stateofbeing_ex 练习）。"""
    return table.find_parent("li") is not None


def table_kind(table: Tag) -> str | None:
    """识别需要保留 HTML 结构与样式的特殊表格。"""
    if is_li_nested_table(table):
        return "li-answer"
    if table.find("a", onclick=re.compile(r"showModal\s*\(")):
        return "kana-stroke"
    if table.find("a", onclick=re.compile(r"playClip\s*\(")):
        return "kana-clip"
    if table.find("a", onclick=re.compile(r"flip\s*\(")):
        return "kana-flip"
    if table.find("td", class_=lambda c: c and "answerline" in c):
        return "practice"
    if table.find("table"):
        return "layout"
    classes = table.get("class") or []
    if "scale-to-page-width" in classes:
        return "layout"
    if "table-condensed" in classes:
        return "grammar"
    if table.find("span", class_=lambda c: c and "hidex" in c):
        return "practice-grid"
    if table.find("caption") or table.find("tr", align="center"):
        return "grammar"
    if table_has_border_style(table):
        return "practice-grid"
    return None


def table_row_class(tr: Tag, kind: str) -> str:
    if tr.get("align") != "center":
        return ""
    if kind in {"kana-stroke", "kana-clip", "kana-flip"}:
        return "jp-kana-row"
    if kind in {"grammar", "practice", "practice-grid"}:
        return "jp-grammar-row"
    return ""


def cell_extra_attrs(cell: Tag) -> str:
    parts: list[str] = []
    for attr in ("rowspan", "colspan", "valign"):
        val = cell.get(attr)
        if val:
            parts.append(f'{attr}="{val}"')
    return (" " + " ".join(parts)) if parts else ""


def render_cell_inner(cell: Tag, kind: str) -> str:
    if cell.find("table", recursive=False):
        chunks: list[str] = []
        for child in cell.children:
            if isinstance(child, Tag) and child.name.lower() == "table":
                chunks.append(render_table(child))
            elif isinstance(child, Tag):
                chunk = inline_children(child)
                if chunk.strip():
                    chunks.append(chunk)
            elif isinstance(child, NavigableString):
                text = html.unescape(str(child)).strip()
                if text:
                    chunks.append(text)
        return "".join(chunks).strip()

    inner = inline_table_cell(cell)
    if kind in {"kana-stroke", "kana-clip", "kana-flip"}:
        inner = wrap_kana_reading_spans(inner)
    return inner


def render_html_table_cell(cell: Tag, kind: str) -> str:
    tag = cell.name.lower()
    cell_classes = list(cell.get("class") or [])
    classes: list[str] = []

    if kind in {"kana-stroke", "kana-clip", "kana-flip"}:
        if "empty" in cell_classes:
            classes.append("jp-kana-empty")
        elif tag == "td" and not render_cell_inner(cell, kind).strip():
            classes.append("jp-kana-empty")

    if "answerline" in cell_classes:
        classes.append("jp-answerline")

    if "toggle" in cell_classes:
        classes.append("jp-toggle")
        if "hidex" in cell_classes:
            classes.append("jp-toggle-answer")

    inner = render_cell_inner(cell, kind)
    extra_classes = [
        c
        for c in cell_classes
        if c not in {"empty", "answerline", "table", "table-condensed", "toggle", "hidex"}
    ]
    all_classes = classes + extra_classes
    class_attr = f' class="{" ".join(dict.fromkeys(all_classes))}"' if all_classes else ""
    content = inner if inner.strip() else "&#160;"
    return f"<{tag}{class_attr}{cell_extra_attrs(cell)}>{content}</{tag}>"


def render_html_table_open(table: Tag, kind: str) -> str:
    cls = TABLE_KIND_CLASSES[kind]
    attrs = [f'class="{cls}"']
    if kind in {"practice", "practice-grid"}:
        border = table.get("border")
        if border:
            attrs.append(f'border="{border}"')
        cellpadding = table.get("cellpadding")
        if cellpadding:
            attrs.append(f'cellpadding="{cellpadding}"')
    return f"<table {' '.join(attrs)}>"


def render_html_table(table: Tag, kind: str) -> str:
    lines = [render_html_table_open(table, kind)]

    caption = table.find("caption", recursive=False)
    if caption:
        cap = inline_children(caption).strip()
        if cap:
            lines.append(f"<caption>{cap}</caption>")

    for tr in table.find_all("tr", recursive=False):
        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        row_cls = table_row_class(tr, kind)
        row_attr = f' class="{row_cls}"' if row_cls else ""
        lines.append(f"<tr{row_attr}>")
        for cell in cells:
            lines.append(render_html_table_cell(cell, kind))
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines) + "\n"


def render_table(table: Tag) -> str:
    kind = table_kind(table)
    if kind:
        return render_html_table(table, kind)

    rows: list[list[str]] = []
    for tr in table.find_all("tr", recursive=False):
        cells = tr.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        rows.append([inline_table_cell(cell) for cell in cells])
    if not rows:
        return ""

    width = max(len(r) for r in rows)
    normalized = [r + [""] * (width - len(r)) for r in rows]
    header = normalized[0]
    body = normalized[1:] if len(normalized) > 1 else []
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * width) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)
