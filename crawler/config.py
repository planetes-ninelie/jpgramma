"""爬虫全局配置与 HTTP 会话。"""

from pathlib import Path

import requests

BASE_URL = "https://res.wokanxing.info/jpgramma/"
ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web" / "grammar"
DATA_DIR = ROOT / "web" / ".vuepress" / "data"
LINK_PREFIX = "/grammar"

SKIP_TAGS = {"script", "style", "nav", "button"}

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": "jpgramma-crawler/1.0 (+https://github.com/jpgramma)",
        "Accept-Language": "zh-Hans,zh;q=0.9",
    }
)
