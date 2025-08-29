from __future__ import annotations

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional, Union
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.enum import StrEnum


class CustomMetadataFieldType(StrEnum):
    String = "string"
    Number = "number"
    Date = "date"


@dataclass_json
@dataclass(frozen=True)
class CustomMetadataFieldRange:
    min: Optional[float] = None
    max: Optional[float] = None


@dataclass_json
@dataclass(frozen=True)
class CustomMetadataField:
    name: str
    type: CustomMetadataFieldType
    range: Optional[CustomMetadataFieldRange] = None
    allowed_values: Optional[Union[list[str], list[float]]] = None
    multiple: Optional[bool] = None
    units: Optional[str] = None
    category: Optional[str] = None
    required: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True)
class CustomMetadata:
    fields: Optional[list[CustomMetadataField]] = None
    categories: Optional[list[str]] = None


@dataclass
class CustomMetadataSchema:
    """Client for getting the Code Ocean custom metadata schema."""

    client: BaseUrlSession

    def get_custom_metadata(self) -> CustomMetadata:
        """Retrieve metadata for a specific capsule by its ID."""
        res = self.client.get("custom_metadata")

        return CustomMetadata.from_dict(res.json())
