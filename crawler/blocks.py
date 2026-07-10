"""块级 HTML 转 Markdown。"""

from __future__ import annotations

import re

from bs4 import NavigableString, Tag

from inline import inline_children
from tables import render_table


def join_li_parts(parts: list[str]) -> str:
    body = ""
    for part in parts:
        if not part:
            continue
        if part == "\n":
            body += "\n"
            continue
        text = part.strip()
        if not text:
            continue
        if body and not body.endswith("\n"):
            body += " "
        body += text
    return re.sub(r" *\n *", "\n", body).strip()


def format_bilingual_body(body: str, *, list_item: bool = False) -> str:
    """日语例句与中文翻译分行：第一行日语，后续行与日语左对齐。"""
    del list_item  # 列表项与段落使用相同对齐，不额外缩进翻译行
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    if len(lines) <= 1:
        return lines[0] if lines else ""
    result = lines[0]
    for trans in lines[1:]:
        result += f'<br>\n<span class="jp-trans">{trans}</span>'
    return result


def format_bilingual_li_body(body: str) -> str:
    return format_bilingual_body(body, list_item=True)


def list_contains_table(tag: Tag) -> bool:
    return any(li.find("table") for li in tag.find_all("li", recursive=False))


def render_list_item_html(li: Tag) -> str:
    parts: list[str] = []
    for child in li.children:
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name in {"ol", "ul"}:
            continue
        if name == "table":
            parts.append(render_table(child).strip())
        elif name == "br":
            parts.append("<br>")
        else:
            chunk = inline_children(child).strip()
            if chunk:
                parts.append(chunk)
    body = "\n".join(parts)
    for sub in li.find_all(["ol", "ul"], recursive=False):
        body = f"{body}\n{render_list(sub, sub.name.lower() == 'ol')}".strip()
    return f"<li>\n{body}\n</li>"


def render_list_html(tag: Tag, ordered: bool) -> str:
    tag_name = "ol" if ordered else "ul"
    items = [render_list_item_html(li) for li in tag.find_all("li", recursive=False)]
    return f"<{tag_name}>\n" + "\n".join(items) + f"\n</{tag_name}>\n"


def render_list(tag: Tag, ordered: bool) -> str:
    if list_contains_table(tag):
        return render_list_html(tag, ordered)

    lines: list[str] = []
    for idx, li in enumerate(tag.find_all("li", recursive=False), start=1):
        prefix = f"{idx}." if ordered else "-"
        parts: list[str] = []
        for child in li.children:
            if isinstance(child, Tag) and child.name.lower() in {"ol", "ul"}:
                continue
            parts.append(inline_children(child))
        body = format_bilingual_li_body(join_li_parts(parts))
        lines.append(f"{prefix} {body}")
        for sub in li.find_all(["ol", "ul"], recursive=False):
            sub_md = render_list(sub, sub.name.lower() == "ol")
            lines.append("\n".join(f"  {line}" for line in sub_md.splitlines()))
    return "\n".join(lines)


def render_exercise_section(tag: Tag) -> str:
    ex_id = tag.get("id", "").strip()
    parts: list[str] = []
    for child in tag.children:
        if isinstance(child, Tag):
            chunk = render_block(child)
            if chunk:
                parts.append(chunk.strip())
    inner = "\n\n".join(parts)
    id_attr = f' id="{ex_id}"' if ex_id else ""
    return f'<div class="jp-exercise"{id_attr}>\n\n{inner}\n\n</div>\n'


def render_block(tag: Tag) -> str:
    name = tag.name.lower()

    if name == "div" and re.fullmatch(r"exercise\d+", tag.get("id") or ""):
        return render_exercise_section(tag)

    if name == "a":
        return inline_children(tag).strip()

    if name in {"h2", "h3", "h4"}:
        level = int(name[1])
        text = inline_children(tag).strip()
        anchor = tag.get("id")
        if anchor:
            return f"{'#' * level} {text} {{#{anchor}}}"
        return f"{'#' * level} {text}"

    if name == "p":
        classes = tag.get("class") or []
        text = format_bilingual_body(inline_children(tag).strip())
        if not text:
            return ""
        if "note2" in classes:
            if text.startswith("译者注"):
                return f"> {text}"
            return f"> **译者注：** {text}"
        return text

    if name == "div" and tag.get("id") == "basic-modal-content":
        return ""

    if name == "div" and "sumbox" in (tag.get("class") or []):
        return render_sumbox(tag)

    if name == "div" and "note" in (tag.get("class") or []):
        text = inline_children(tag).strip()
        if text.startswith("译者注"):
            return f"> {text}"
        return f"> **译者注：** {text}"

    if name in {"ol", "ul"}:
        return render_list(tag, name == "ol")

    if name == "table":
        return render_table(tag)

    if name == "iframe":
        src = tag.get("src", "")
        if "youtube.com" in src or "youtu.be" in src:
            return f'\n<iframe class="youtube" src="{src}" frameborder="0" allowfullscreen></iframe>\n'
        return ""

    if name == "hr":
        return "---"

    chunks: list[str] = []
    for child in tag.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                chunks.append(text)
        elif isinstance(child, Tag):
            chunk = render_block(child)
            if chunk:
                chunks.append(chunk)
    return "\n\n".join(chunks)


def render_sumbox(tag: Tag) -> str:
    summary_el = tag.find("span", class_="summary")
    title = ""
    if summary_el:
        title = "".join(summary_el.stripped_strings)

    classes = ["sumbox"]
    if (tag.get("align") or "").lower() == "center":
        classes.append("sumbox--center")

    lines = [f'<div class="{" ".join(classes)}">']
    if title:
        lines.extend([f'<div class="sumbox-title">{title}</div>', ""])
    for child in tag.children:
        if isinstance(child, NavigableString):
            text = re.sub(r"\s+", " ", str(child))
            if text.strip():
                lines.append(text)
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name.lower()
        if name == "span" and "summary" in (child.get("class") or []):
            continue
        if name in {"ol", "ul"}:
            lines.append(render_list(child, name == "ol"))
        elif name == "table":
            lines.append(render_table(child))
        elif name == "a":
            lines.append(inline_children(child))
        else:
            chunk = render_block(child)
            if chunk:
                lines.append(chunk)
    lines.append("</div>")
    return "\n".join(lines) + "\n"
