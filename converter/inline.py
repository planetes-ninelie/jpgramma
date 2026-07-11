"""行内 HTML 节点转 Markdown / 保留 HTML 片段。"""

from __future__ import annotations

import html
import re

from bs4 import NavigableString, Tag

from config import SKIP_TAGS
from urls import html_path_to_link, parse_anchor_onclick, parse_exercise_onclick


def inline_children(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", html.unescape(str(node)))
    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()
    if name in SKIP_TAGS:
        return ""

    if name == "div" and "tooltip" in (node.get("class") or []):
        return ""

    if name == "br":
        return "\n"

    if name == "iframe":
        src = node.get("src", "")
        if "youtube.com" in src or "youtu.be" in src:
            return f'\n<iframe class="youtube" src="{src}" frameborder="0" allowfullscreen></iframe>\n'
        return ""

    if name == "span" and "answerline" in (node.get("class") or []):
        parts: list[str] = []
        for child in node.children:
            if isinstance(child, NavigableString):
                parts.append(html.unescape(str(child)))
            elif isinstance(child, Tag):
                parts.append(inline_children(child))
        inner = "".join(parts)
        return f'<span class="jp-answerline">{inner}</span>'

    if name == "span" and "hidex" in (node.get("class") or []):
        text = "".join(inline_children(c) for c in node.children).strip()
        elem_id = node.get("id", "").strip()
        id_attr = f' id="{elem_id}"' if elem_id else ""
        return f'<span class="jp-hidex"{id_attr}>{text}</span>'

    if name == "span" and "popup" in (node.get("class") or []):
        text = "".join(inline_children(c) for c in node.children).strip()
        title = node.get("title", "").strip()
        if title:
            return f'<span class="jp-word" title="{title}">{text}</span>'
        return text

    if name in {"em", "i"}:
        inner = "".join(inline_children(c) for c in node.children).strip()
        return f"<{name}>{inner}</{name}>" if inner else ""

    if name in {"strong", "b"}:
        inner = "".join(inline_children(c) for c in node.children).strip()
        return f"<{name}>{inner}</{name}>" if inner else ""

    if name == "u":
        inner = "".join(inline_children(c) for c in node.children).strip()
        return f"<u>{inner}</u>" if inner else ""

    if name == "a":
        href = node.get("href", "")
        inner = "".join(inline_children(c) for c in node.children).strip()
        if not inner:
            return ""
        onclick = node.get("onclick", "")
        action = parse_anchor_onclick(onclick)
        if action:
            kind, target = action
            if kind == "showModal":
                return f'<a class="jp-stroke" href="#" data-char="{target}">{inner}</a>'
            if kind == "playClip":
                return f'<a class="jp-clip" href="#" data-char="{target}">{inner}</a>'
            if kind == "flip":
                return f'<a class="jp-flip" href="#" data-flip="{target}">{inner}</a>'
        exercise_action = parse_exercise_onclick(onclick)
        if exercise_action:
            kind, target = exercise_action
            if kind == "show":
                return f'<a class="jp-answer-show" href="#" data-exercise="{target}">{inner}</a>'
            if kind == "hide":
                return f'<a class="jp-answer-hide" href="#" data-exercise="{target}">{inner}</a>'
            if kind == "toggle-hidex":
                return f'<a class="jp-answer-toggle" href="#" data-exercise="{target}">{inner}</a>'
            if kind == "toggle-columns":
                return f'<a class="jp-column-toggle" href="#" data-exercise="{target}">{inner}</a>'
        if href.startswith("javascript:"):
            return inner
        link = html_path_to_link(href)
        if link.startswith("http") or link.startswith("mailto:"):
            return f"[{inner}]({link})"
        return f"[{inner}]({link})"

    if name == "code":
        inner = "".join(inline_children(c) for c in node.children).strip()
        return f"`{inner}`"

    return "".join(inline_children(c) for c in node.children)


def inline_table_cell(cell: Tag) -> str:
    parts: list[str] = []
    for child in cell.children:
        if isinstance(child, NavigableString):
            text = re.sub(r"\s+", " ", html.unescape(str(child))).strip()
            if text:
                parts.append(text)
            continue
        if not isinstance(child, Tag):
            continue
        if child.name.lower() == "br":
            parts.append("<br>")
            continue
        parts.append(inline_children(child))
    return "".join(parts).strip()
