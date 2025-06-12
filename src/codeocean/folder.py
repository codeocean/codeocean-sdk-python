from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import Optional


@dataclass_json
@dataclass(frozen=True)
class FolderItem:
    """Represents a file or folder item within a folder listing."""

    name: str = field(metadata={"description": "Name of the file or folder"})
    path: str = field(metadata={"description": "Path of the file or folder"})
    type: str = field(metadata={"description": "Item type ('file' or 'folder')"})
    size: Optional[int] = field(
        default=None, metadata={"description": "Size in bytes (only for files)"}
    )


@dataclass_json
@dataclass(frozen=True)
class Folder:
    """Represents a folder with its list of items (files and subfolders)."""

    items: list[FolderItem] = field(
        metadata={"description": "List of items in the folder (files and subfolders)"}
    )


@dataclass_json
@dataclass(frozen=True)
class ListFolderParams:
    """Parameters for listing contents of a folder."""

    path: str = field(
        metadata={"description": "Path of the folder to list; empty string for root"}
    )


@dataclass_json
@dataclass(frozen=True)
class DownloadFileURL:
    """Download URL information for retrieving a file."""

    url: str = field(
        metadata={"description": "Pre-signed URL for downloading the specified file"}
    )
