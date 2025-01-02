from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from typing import Optional


@dataclass_json
@dataclass(frozen=True)
class FolderItem:
    name: str
    path: str
    type: str
    size: Optional[int] = None


@dataclass_json
@dataclass(frozen=True)
class Folder:
    items: list[FolderItem]


@dataclass_json
@dataclass(frozen=True)
class ListFolderParams:
    path: str


@dataclass_json
@dataclass(frozen=True)
class DownloadFileURL:
    url: str
    