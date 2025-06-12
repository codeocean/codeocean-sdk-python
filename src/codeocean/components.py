from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import Optional

from codeocean.enum import StrEnum


class UserRole(StrEnum):
    """Role levels for user permissions in Code Ocean resources."""
    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"


@dataclass_json
@dataclass(frozen=True)
class UserPermissions:
    """User permission configuration with email and role assignment."""
    email: str = field(metadata={"description": "User email address for permission assignment"})
    role: UserRole = field(metadata={"description": "Permission level granted to the user (owner, editor, viewer)"})


class GroupRole(StrEnum):
    """Role levels for group permissions in Code Ocean resources."""
    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"
    Discoverable = "discoverable"


@dataclass_json
@dataclass(frozen=True)
class GroupPermissions:
    """Group permission configuration with group identifier and role assignment."""
    group: str = field(metadata={"description": "Group identifier for permission assignment"})
    role: GroupRole = field(metadata={"description": "Permission level granted to the group (owner, editor, viewer, discoverable)"})


class EveryoneRole(StrEnum):
    """Role levels for public access permissions in Code Ocean resources."""
    Viewer = "viewer"
    Discoverable = "discoverable"
    None_ = "none"


@dataclass_json
@dataclass(frozen=True)
class Permissions:
    """Complete permission configuration for Code Ocean resources including users, groups, and public access."""
    users: Optional[list[UserPermissions]] = field(default=None, metadata={"description": "List of user-specific permissions"})
    groups: Optional[list[GroupPermissions]] = field(default=None, metadata={"description": "List of group-specific permissions"})
    everyone: Optional[EveryoneRole] = field(default=None, metadata={"description": "Public access level (viewer, discoverable, none)"})
    share_assets: Optional[bool] = field(default=None, metadata={"description": "Whether to share associated assets with granted permissions"})


class SortOrder(StrEnum):
    """Sort order options for search and listing operations."""
    Ascending = "asc"
    Descending = "desc"


@dataclass_json
@dataclass(frozen=True)
class SearchFilterRange:
    """Numeric range filter for search operations with minimum and maximum values."""
    min: float = field(metadata={"description": "Minimum value for range filter"})
    max: float = field(metadata={"description": "Maximum value for range filter"})


@dataclass_json
@dataclass(frozen=True)
class SearchFilter:
    """Search filter configuration for field-level filtering with various value types and range support."""
    key: str = field(metadata={"description": "Field name to filter on (name, description, tags, or custom field key)"})
    value: Optional[str | float] = field(default=None, metadata={"description": "Single field value to include/exclude"})
    values: Optional[list[str | float]] = field(default=None, metadata={"description": "Multiple field values for inclusion/exclusion"})
    range: Optional[SearchFilterRange] = field(default=None, metadata={"description": "Numeric range filter (only one of min/max must be set)"})
    exclude: Optional[bool] = field(default=None, metadata={"description": "Whether to include (false) or exclude (true) the specified values"})


class Ownership(StrEnum):
    """Ownership filter options for search operations."""
    Private = "private"
    Shared = "shared"
    Created = "created"
