"""站内链接与 slug 转换。"""

from __future__ import annotations

import re

from config import LINK_PREFIX


def filename_to_slug(filename: str) -> str:
    """与 Plume permalink: 'filepath' 的 slug 规则保持一致。"""
    slug = filename.replace("_", "-")
    return re.sub(r"(\D)(\d+)$", r"\1-\2", slug)


def page_path_to_url(page: str, anchor: str = "") -> str:
    page = page.strip("/")
    if page in ("", "index"):
        page = "guide"
    else:
        page = filename_to_slug(page.split("/")[-1].removesuffix(".html"))
    url = f"{LINK_PREFIX}/{page}/"
    return f"{url}#{anchor}" if anchor else url


def html_path_to_link(href: str) -> str:
    href = href.strip()
    if not href or href.startswith("http") or href.startswith("mailto:"):
        return href
    href = href.split("?")[0]
    path, _, anchor = href.partition("#")
    if path.endswith(".html"):
        path = path[:-5]
    if path.startswith(LINK_PREFIX):
        path = path[len(LINK_PREFIX) :]
    path = path.strip("/")
    if path in ("", "index"):
        return page_path_to_url("guide", anchor)
    return page_path_to_url(path, anchor)


def parse_anchor_onclick(onclick: str) -> tuple[str, str] | None:
    """解析 showModal / playClip / flip 等 onclick。"""
    if not onclick:
        return None
    match = re.search(r"(showModal|playClip|flip)\s*\(\s*['\"]([^'\"]+)['\"]", onclick)
    if not match:
        return None
    return match.group(1), match.group(2)


def parse_exercise_onclick(onclick: str) -> tuple[str, str] | None:
    """解析练习页显示/隐藏答案 onclick，返回 (action, exercise_id)。"""
    if not onclick:
        return None
    match = re.search(
        r"\$\(\s*['\"]#([^'\"]+)\s+\.hidex['\"]\s*\)\.(fadeIn|fadeOut)\s*\(\s*\)",
        onclick,
    )
    if match:
        action = "show" if match.group(2) == "fadeIn" else "hide"
        return action, match.group(1)
    match = re.search(r"toggleAll\s*\(\s*['\"]([^'\"]+)['\"]", onclick)
    if match:
        return "toggle-hidex", match.group(1)
    match = re.search(r"\btoggle\s*\(\s*['\"]([^'\"]+)['\"]", onclick)
    if match:
        return "toggle-columns", match.group(1)
    return None
