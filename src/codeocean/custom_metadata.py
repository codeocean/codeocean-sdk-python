from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from dataclasses_json import dataclass_json
from typing import Optional, Union
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.enum import StrEnum


class CustomMetadataFieldType(StrEnum):
    """ Type of the custom metadata field value. """

    String = "string"
    Number = "number"
    Date = "date"


@dataclass_json
@dataclass(frozen=True)
class CustomMetadataFieldRange:
    """ Range of valid values for a custom metadata field. """

    min: Optional[float] = dataclass_field(
        default=None,
        metadata={"description": "Minimum valid value"}
    )
    max: Optional[float] = dataclass_field(
        default=None,
        metadata={"description": "Maximum valid value"}
    )


@dataclass_json
@dataclass(frozen=True)
class CustomMetadataField:
    """ Represents a custom metadata field in the Code Ocean platform. """

    name: str = dataclass_field(
        metadata={"description": "Name of the custom metadata field"}
    )
    type: CustomMetadataFieldType = dataclass_field(
        metadata={"description": "Type of the custom metadata field value (string, number, date)"}
    )
    range: Optional[CustomMetadataFieldRange] = dataclass_field(
        default=None,
        metadata={"description": "Range of valid values for the field"}
    )
    allowed_values: Optional[Union[list[str], list[float]]] = dataclass_field(
        default=None,
        metadata={"description": "Allowed values for the field (item type according to field type)"}
    )
    multiple: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Whether multiple values are allowed"}
    )
    units: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Units of the field value"}
    )
    category: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Category of the field"}
    )
    required: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Whether the field is required"}
    )


@dataclass_json
@dataclass(frozen=True)
class CustomMetadata:
    """ Represents the custom metadata schema in the Code Ocean platform. """

    fields: Optional[list[CustomMetadataField]] = dataclass_field(
        default=None,
        metadata={"description": "List of custom metadata fields"}
    )
    categories: Optional[list[str]] = dataclass_field(
        default=None,
        metadata={"description": "List of categories for custom metadata fields"}
    )


@dataclass
class CustomMetadataSchema:
    """Client for getting the Code Ocean custom metadata schema."""

    client: BaseUrlSession

    def get_custom_metadata(self) -> CustomMetadata:
        """Retrieve the Code Ocean deployment's custom metadata schema."""
        res = self.client.get("custom_metadata")

        return CustomMetadata.from_dict(res.json())
