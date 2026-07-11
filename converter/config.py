"""HTML → Markdown 转换器配置。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "source"
WEB_DIR = ROOT / "web" / "grammar"
DATA_DIR = ROOT / "web" / ".vuepress" / "data"
LINK_PREFIX = "/grammar"

SKIP_TAGS = {"script", "style", "nav", "button"}
