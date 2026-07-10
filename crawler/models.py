"""爬虫数据结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SidebarItem:
    text: str
    link: str | None = None
    items: list[SidebarItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"text": self.text}
        if self.link:
            result["link"] = self.link
        if self.items:
            result["items"] = [item.to_dict() for item in self.items]
        return result


@dataclass
class AppendixEntry:
    kana: str
    title: str
    link: str
    anchor: str = ""
