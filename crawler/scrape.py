#!/usr/bin/env python3
"""抓取 Tae Kim 日语语法指南（中文译本）并转换为 Markdown。"""

from __future__ import annotations

import time

from appendix import (
    appendix_to_markdown,
    collect_page_slugs,
    parse_appendix,
    parse_sidebar_from_index,
    write_search_meta,
    write_sidebar_config,
)
from config import LINK_PREFIX, WEB_DIR
from fetch import collect_stroke_chars, download_stroke_assets, fetch_html
from page import page_to_markdown


def scrape() -> None:
    print("正在获取目录页…")
    index_html = fetch_html("index.html")
    appendix_html = fetch_html("appendix.html")

    slugs = collect_page_slugs(index_html, appendix_html)
    print(f"共发现 {len(slugs)} 个内容页面")

    sidebar = parse_sidebar_from_index(index_html)
    appendix_entries = parse_appendix(appendix_html)

    for stale in ("markdown-examples.md", "api-examples.md"):
        path = WEB_DIR / stale
        if path.exists():
            path.unlink()

    WEB_DIR.mkdir(parents=True, exist_ok=True)

    _, guide_md = page_to_markdown(index_html, "guide")
    (WEB_DIR / "guide.md").write_text(guide_md, encoding="utf-8")

    appendix_md = appendix_to_markdown(appendix_entries)
    (WEB_DIR / "appendix.md").write_text(appendix_md, encoding="utf-8")

    write_sidebar_config(sidebar, f"{LINK_PREFIX}/appendix")
    write_search_meta(appendix_entries)

    stroke_chars: set[str] = set()
    ok, failed = 0, []
    for i, slug in enumerate(slugs, start=1):
        out = WEB_DIR / f"{slug}.md"
        try:
            print(f"[{i}/{len(slugs)}] {slug}")
            html = fetch_html(f"{slug}.html")
            stroke_chars.update(collect_stroke_chars(html))
            _, md = page_to_markdown(html, slug)
            out.write_text(md, encoding="utf-8")
            ok += 1
            time.sleep(0.35)
        except Exception as exc:  # noqa: BLE001
            failed.append((slug, str(exc)))
            print(f"  ! 失败: {exc}")

    print(f"\n完成：成功 {ok}，失败 {len(failed)}")
    if failed:
        for slug, err in failed:
            print(f"  - {slug}: {err}")

    download_stroke_assets(stroke_chars)


if __name__ == "__main__":
    scrape()
