from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import Optional

from codeocean.enum import StrEnum


class UserRole(StrEnum):
    """Role levels for user permissions of Code Ocean resources."""

    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"


@dataclass_json
@dataclass(frozen=True)
class UserPermissions:
    """User permission configuration with email and role assignment."""

    email: str = field(
        metadata={"description": "User email address for permission assignment"},
    )
    role: UserRole = field(
        metadata={
            "description": "Permission level granted to the user (owner, editor, or viewer)",
        },
    )


class GroupRole(StrEnum):
    """Role levels for group permissions of Code Ocean resources."""

    Owner = "owner"
    Editor = "editor"
    Viewer = "viewer"
    Discoverable = "discoverable"


@dataclass_json
@dataclass(frozen=True)
class GroupPermissions:
    """Group permission configuration with group identifier and role assignment."""

    group: str = field(
        metadata={"description": "Group identifier for permission assignment"},
    )
    role: GroupRole = field(
        metadata={
            "description": "Permission level granted to the group (owner, editor, viewer, or discoverable)",
        },
    )


class EveryoneRole(StrEnum):
    """Role levels for public access permissions of Code Ocean resources."""

    Viewer = "viewer"
    Discoverable = "discoverable"
    None_ = "none"


@dataclass_json
@dataclass(frozen=True)
class Permissions:
    """Complete permission configuration for Code Ocean resources including users, groups, and public access."""

    users: Optional[list[UserPermissions]] = field(
        default=None,
        metadata={"description": "List of user-specific permissions"},
    )
    groups: Optional[list[GroupPermissions]] = field(
        default=None,
        metadata={"description": "List of group-specific permissions"},
    )
    everyone: Optional[EveryoneRole] = field(
        default=None,
        metadata={"description": "Public access level (viewer, discoverable, or none)"},
    )
    share_assets: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Whether to share all related assets (attached data assets and "
            "pipeline capsules) with added users and groups",
        },
    )


class SortOrder(StrEnum):
    """Sort order options for search operations."""

    Ascending = "asc"
    Descending = "desc"


@dataclass_json
@dataclass(frozen=True)
class SearchFilterRange:
    """Numeric range filter for search operations with minimum and maximum values."""

    min: float = field(
        metadata={"description": "Minimum value for range filter"},
    )
    max: float = field(
        metadata={"description": "Maximum value for range filter"},
    )


@dataclass_json
@dataclass(frozen=True)
class SearchFilter:
    """Search filter configuration for field-level filtering with various value types and range support."""

    key: str = field(
        metadata={
            "description": "Field name to filter on (name, description, tags, or custom field key)",
        },
    )
    value: Optional[str | float] = field(
        default=None,
        metadata={"description": "Single field value to include/exclude"},
    )
    values: Optional[list[str | float]] = field(
        default=None,
        metadata={"description": "Multiple field values for inclusion/exclusion"},
    )
    range: Optional[SearchFilterRange] = field(
        default=None,
        metadata={
            "description": "Numeric range filter (only one of min/max must be set)",
        },
    )
    exclude: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Whether to include (false) or exclude (true) the specified values",
        },
    )


class Ownership(StrEnum):
    """Ownership filter options for search operations."""

    Private = "private"
    Shared = "shared"
    Created = "created"


class AppPanelDataAssetKind(StrEnum):
    """The kind of data asset displayed in an app panel.

    - 'Internal' → Data stored inside Code Ocean.
    - 'External' → Data stored external to Code Ocean.
    - 'Combined' → Data containing multiple external data assets.

    In pipelines, a data asset can only be replaced with one of the same kind.
    """

    Internal = "internal"
    External = "external"
    Combined = "combined"


class AppPanelParameterType(StrEnum):
    """The type of parameter displayed in an app panel."""

    Text = "text"
    List = "list"
    File = "file"


@dataclass_json
@dataclass(frozen=True)
class AppPanelCategories:
    """Categories for a capsule's App Panel parameters."""

    id: str = field(
        metadata={"description": "Unique identifier for the category."},
    )
    name: str = field(
        metadata={"description": "Human-readable name of the category."},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Optional detailed description of the category."},
    )
    help_text: Optional[str] = field(
        default=None,
        metadata={"description": "Optional help text providing guidance or additional information about the category."},
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanelParameters:
    """Parameters for a capsule's App Panel."""

    name: str = field(
        metadata={"description": "Parameter label/display name."}
    )
    type: AppPanelParameterType = field(
        metadata={"description": "Type of the parameter (text, list, file)."}
    )
    category: Optional[str] = field(
        default=None,
        metadata={"description": "ID of category the parameter belongs to."}
    )
    param_name: Optional[str] = field(
        default=None,
        metadata={"description": "The parameter name/argument key"}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Description of the parameter."}
    )
    help_text: Optional[str] = field(
        default=None,
        metadata={"description": "Help text for the parameter."}
    )
    value_type: Optional[str] = field(
        default=None,
        metadata={"description": "Value type of the parameter."}
    )
    default_value: Optional[str] = field(
        default=None,
        metadata={"description": "Default value of the parameter."}
    )
    required: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the parameter is required."}
    )
    hidden: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the parameter is hidden."}
    )
    minimum: Optional[float] = field(
        default=None,
        metadata={"description": "Minimum value for the parameter."}
    )
    maximum: Optional[float] = field(
        default=None,
        metadata={"description": "Maximum value for the parameter."}
    )
    pattern: Optional[str] = field(
        default=None,
        metadata={"description": "Regular expression pattern for the parameter."}
    )
    value_options: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Allowed values for the parameter."}
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanelGeneral:
    """General information about a capsule's App Panel."""

    title: Optional[str] = field(
        default=None,
        metadata={"description": "Title of the App Panel."}
    )
    instructions: Optional[str] = field(
        default=None,
        metadata={"description": "Instructions for using the App Panel."}
    )
    help_text: Optional[str] = field(
        default=None,
        metadata={"description": "Help text for the App Panel."}
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanelDataAsset:
    """Data asset parameter for the App Panel."""

    id: str = field(
        metadata={"description": "Unique identifier for the data asset."}
    )
    mount: str = field(
        metadata={"description": "Mount path of the data asset within the capsule. "
                  "Use this mount path to replace the currently attached data asset with your own"}
    )
    name: str = field(
        metadata={"description": "Display name of the data asset."}
    )
    kind: AppPanelDataAssetKind = field(
        metadata={"description": "Kind of the data asset (internal, external, combined)."}
    )
    accessible: bool = field(
        metadata={"description": "Indicates if the data asset is accessible to the user."}
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Optional description of the data asset parameter."}
    )
    help_text: Optional[str] = field(
        default=None,
        metadata={"description": "Optional help text for the data asset parameter."}
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanelResult:
    """Selected result files to display once the computation is complete."""

    file_name: str = field(
        metadata={"description": "Name of the result file."}
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanelProcess:
    """Pipeline process name and its corresponding app panel (for pipelines of capsules only)"""

    name: str = field(
        metadata={"description": "Name of the pipeline process."}
    )
    categories: Optional[AppPanelCategories] = field(
        default=None,
        metadata={"description": "Categories for the pipeline process's app panel parameters."}
    )
    parameters: Optional[AppPanelParameters] = field(
        default=None,
        metadata={"description": "Parameters for the pipeline process's app panel."}
    )


@dataclass_json
@dataclass(frozen=True)
class AppPanel:
    """App Panel configuration for a capsule or pipeline, including general info, data assets,
    categories, parameters, and results.
    """

    general: Optional[AppPanelGeneral] = field(
        default=None,
        metadata={"description": "General information about the App Panel."}
    )
    data_assets: Optional[list[AppPanelDataAsset]] = field(
        default=None,
        metadata={"description": "List of data assets used in the App Panel."}
    )
    categories: Optional[list[AppPanelCategories]] = field(
        default=None,
        metadata={"description": "Categories for organizing App Panel parameters."}
    )
    parameters: Optional[list[AppPanelParameters]] = field(
        default=None,
        metadata={"description": "Parameters for the App Panel."}
    )
    results: Optional[list[AppPanelResult]] = field(
        default=None,
        metadata={"description": "Result files to display after computation."}
    )
    processes: Optional[list[AppPanelProcess]] = field(
        default=None,
        metadata={"description": "Pipeline processes and their App Panels."}
    )
