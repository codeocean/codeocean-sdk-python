from dataclasses_json import dataclass_json
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional


class UserRole(StrEnum):
    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"


@dataclass_json
@dataclass(frozen=True)
class UserPermissions:
    email: str
    role: UserRole


class GroupRole(StrEnum):
    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"
    Discoverable = "discoverable"


@dataclass_json
@dataclass(frozen=True)
class GroupPermissions:
    group: str
    role: GroupRole


class EveryoneRole(StrEnum):
    Viewer = "viewer"
    Discoverable = "discoverable"
    None_ = "none"


@dataclass_json
@dataclass(frozen=True)
class Permissions:
    users: Optional[list[UserPermissions]] = None
    groups: Optional[list[GroupPermissions]] = None
    everyone: Optional[EveryoneRole] = None
    share_assets: Optional[bool] = None


class SortOrder(StrEnum):
    Ascending = "asc"
    Descending = "desc"


@dataclass_json
@dataclass(frozen=True)
class SearchFilterRange:
    min: float
    max: float


@dataclass_json
@dataclass(frozen=True)
class SearchFilter:
    key: str
    value: Optional[str | float] = None
    values: Optional[list[str | float]] = None
    range: Optional[SearchFilterRange] = None
    exclude: Optional[bool] = None
