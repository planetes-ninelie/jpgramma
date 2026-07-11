"""从源码仓库读取 HTML 与复制静态资源。"""

import re
import shutil

from config import ROOT, SOURCE_DIR


def read_html(path: str) -> str:
    source_path = SOURCE_DIR / path
    if not source_path.is_file():
        raise FileNotFoundError(f"源文件不存在: {source_path}")
    return source_path.read_text(encoding="utf-8")


def collect_stroke_chars(html: str) -> set[str]:
    chars = set(re.findall(r"showModal\s*\(\s*['\"]([^'\"]+)['\"]", html))
    chars.update(re.findall(r"playClip\s*\(\s*['\"]([^'\"]+)['\"]", html))
    return chars


def copy_stroke_assets(chars: set[str]) -> None:
    if not chars:
        return

    img_dir = ROOT / "web" / ".vuepress" / "public" / "images" / "hiragana"
    audio_dir = ROOT / "web" / ".vuepress" / "public" / "audio"
    img_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在从源码复制 {len(chars)} 个假名笔顺/发音资源…")
    for char in sorted(chars):
        mappings = [
            (SOURCE_DIR / "images" / "hiragana" / f"{char}.gif", img_dir / f"{char}.gif"),
            (SOURCE_DIR / "audio" / f"{char}.ogg", audio_dir / f"{char}.ogg"),
            (SOURCE_DIR / "audio" / f"{char}.mp3", audio_dir / f"{char}.mp3"),
        ]
        for src, dest in mappings:
            if not src.is_file():
                continue
            if dest.exists() and dest.stat().st_size == src.stat().st_size:
                continue
            shutil.copy2(src, dest)
