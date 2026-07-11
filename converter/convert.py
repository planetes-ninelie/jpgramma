#!/usr/bin/env python3
"""从 pizzamx/jpgramma 源码仓库将 HTML 转换为 Markdown。"""

from __future__ import annotations

from appendix import (
    appendix_to_markdown,
    collect_page_slugs,
    parse_appendix,
    parse_sidebar_from_index,
    write_search_meta,
    write_sidebar_config,
)
from config import LINK_PREFIX, SOURCE_DIR, WEB_DIR
from page import page_to_markdown
from source import collect_stroke_chars, copy_stroke_assets, read_html


def convert() -> None:
    if not SOURCE_DIR.is_dir():
        raise SystemExit(
            f"源码目录不存在: {SOURCE_DIR}\n"
            "请先执行: git submodule update --init --recursive"
        )

    print("正在读取源码目录…")
    index_html = read_html("index.html")
    appendix_html = read_html("appendix.html")

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
            html = read_html(f"{slug}.html")
            stroke_chars.update(collect_stroke_chars(html))
            _, md = page_to_markdown(html, slug)
            out.write_text(md, encoding="utf-8")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed.append((slug, str(exc)))
            print(f"  ! 失败: {exc}")

    print(f"\n完成：成功 {ok}，失败 {len(failed)}")
    if failed:
        for slug, err in failed:
            print(f"  - {slug}: {err}")

    copy_stroke_assets(stroke_chars)


if __name__ == "__main__":
    convert()
