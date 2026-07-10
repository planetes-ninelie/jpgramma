"""页面级 HTML 提取与 Markdown 组装。"""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup, Tag

from blocks import render_block


def extract_main_blocks(soup: BeautifulSoup) -> tuple[str, list[Tag]]:
    title_el = soup.select_one("h1#page-title")
    if not title_el:
        raise ValueError("页面缺少 h1#page-title")

    title = title_el.get_text(strip=True)
    blocks: list[Tag] = []
    for sib in title_el.next_siblings:
        if not isinstance(sib, Tag):
            continue
        if sib.name == "p" and "作者" in sib.get_text():
            continue
        if sib.get("class") and "menu" in sib.get("class"):
            break
        if sib.name == "nav" and "footer" in (sib.get("class") or []):
            break
        blocks.append(sib)
    return title, blocks


def blocks_to_markdown(blocks: list[Tag]) -> str:
    parts: list[str] = []
    for block in blocks:
        if block.name == "nav":
            continue
        md = render_block(block)
        if md:
            parts.append(md.strip())
    text = "\n\n".join(parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_to_markdown(html: str, slug: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    title, blocks = extract_main_blocks(soup)
    body = blocks_to_markdown(blocks)

    frontmatter = {
        "title": title,
        "outline": "deep",
    }
    fm_lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in frontmatter.items()] + ["---"]
    return title, "\n".join(fm_lines) + "\n\n" + body + "\n"
