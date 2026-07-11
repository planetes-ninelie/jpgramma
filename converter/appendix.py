"""侧边栏、附录索引与站点元数据输出。"""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup, Tag

from config import DATA_DIR, LINK_PREFIX
from models import AppendixEntry, SidebarItem
from urls import html_path_to_link, page_path_to_url


def parse_sidebar_from_index(html: str) -> list[SidebarItem]:
    soup = BeautifulSoup(html, "lxml")
    root_ol = None
    for h2 in soup.find_all("h2"):
        if "目录" in h2.get_text():
            root_ol = h2.find_next_sibling("ol")
            break
    if not root_ol:
        return []

    def walk_list(ol: Tag) -> list[SidebarItem]:
        items: list[SidebarItem] = []
        for li in ol.find_all("li", recursive=False):
            link = li.find("a", recursive=False)
            if link:
                text = link.get_text(strip=True)
                href = html_path_to_link(link.get("href", ""))
                child_ul = link.find_next_sibling("ul")
                if child_ul:
                    items.append(SidebarItem(text=text, link=href, items=walk_list(child_ul)))
                else:
                    items.append(SidebarItem(text=text, link=href))
            else:
                text = li.get_text(strip=True)
                child_ul = li.find("ul", recursive=False)
                if child_ul:
                    items.append(SidebarItem(text=text, items=walk_list(child_ul)))
        return items

    return walk_list(root_ol)


def parse_appendix(html: str) -> list[AppendixEntry]:
    soup = BeautifulSoup(html, "lxml")
    entries: list[AppendixEntry] = []
    content = soup.select_one("#content-area") or soup
    for li in content.select("ul > li"):
        kana = ""
        first = li.find(string=True, recursive=False)
        if first:
            kana = str(first).strip()
        ol = li.find("ol")
        if not ol:
            continue
        for a in ol.find_all("a"):
            href = a.get("href", "")
            if not href.endswith(".html") and ".html#" not in href:
                continue
            path, _, anchor = href.partition("#")
            entries.append(
                AppendixEntry(
                    kana=kana,
                    title=a.get_text(strip=True),
                    link=html_path_to_link(path),
                    anchor=anchor,
                )
            )
    return entries


def appendix_to_markdown(entries: list[AppendixEntry]) -> str:
    lines = [
        "---",
        'title: "语法索引（五十音）"',
        "outline: deep",
        "---",
        "",
        "按五十音排列的语法点速查索引，点击可跳转到对应章节。",
        "",
        "::: tip 使用搜索",
        "也可以按 `Ctrl/Cmd + K` 打开全站搜索，支持中文、日文和罗马音关键词。",
        ":::",
        "",
    ]
    current_kana = ""
    for entry in entries:
        if entry.kana and entry.kana != current_kana:
            current_kana = entry.kana
            lines.append(f"## {current_kana}")
            lines.append("")
        target = page_path_to_url(
            entry.link.removeprefix(LINK_PREFIX).strip("/"),
            entry.anchor,
        )
        lines.append(f"- [{entry.title}]({target})")
    lines.append("")
    return "\n".join(lines)


def collect_page_slugs(index_html: str, appendix_html: str) -> list[str]:
    slugs: set[str] = set()
    for html in (index_html, appendix_html):
        for match in re.findall(r'href="([^"?#]+\.html)"', html):
            slugs.add(match.replace(".html", ""))
    slugs.discard("index")
    slugs.discard("appendix")
    return sorted(slugs)


def write_sidebar_config(sidebar: list[SidebarItem], appendix_link: str) -> None:
    sidebar_data = [item.to_dict() for item in sidebar]
    sidebar_data.append({"text": "语法索引", "link": f"{LINK_PREFIX}/appendix"})
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "sidebar.json").write_text(
        json.dumps(sidebar_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_search_meta(entries: list[AppendixEntry]) -> None:
    payload = [
        {
            "title": e.title,
            "link": f"{e.link}#{e.anchor}" if e.anchor else e.link,
            "kana": e.kana,
        }
        for e in entries
    ]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "appendix-index.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
