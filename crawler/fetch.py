"""HTTP 抓取与静态资源下载。"""

import re
import time
from urllib.parse import urljoin

import requests

from config import BASE_URL, ROOT, SESSION


def fetch_html(path: str) -> str:
    url = urljoin(BASE_URL, path)
    for attempt in range(3):
        try:
            resp = SESSION.get(url, timeout=30)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding or "utf-8"
            return resp.text
        except requests.RequestException:
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"无法获取 {url}")


def collect_stroke_chars(html: str) -> set[str]:
    chars = set(re.findall(r"showModal\s*\(\s*['\"]([^'\"]+)['\"]", html))
    chars.update(re.findall(r"playClip\s*\(\s*['\"]([^'\"]+)['\"]", html))
    return chars


def download_stroke_assets(chars: set[str]) -> None:
    if not chars:
        return

    img_dir = ROOT / "web" / ".vuepress" / "public" / "images" / "hiragana"
    audio_dir = ROOT / "web" / ".vuepress" / "public" / "audio"
    img_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)

    print(f"正在下载 {len(chars)} 个假名笔顺/发音资源…")
    for char in sorted(chars):
        targets = [
            (img_dir / f"{char}.gif", f"images/hiragana/{char}.gif"),
            (audio_dir / f"{char}.ogg", f"audio/{char}.ogg"),
            (audio_dir / f"{char}.mp3", f"audio/{char}.mp3"),
        ]
        for dest, remote in targets:
            if dest.exists() and dest.stat().st_size > 0:
                continue
            try:
                resp = SESSION.get(urljoin(BASE_URL, remote), timeout=30)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
            except requests.RequestException as exc:
                print(f"  跳过 {remote}: {exc}")
