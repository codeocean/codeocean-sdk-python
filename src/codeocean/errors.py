from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Type, TypeVar, Dict, Any
import requests

T = TypeVar("T", bound="Error")


@dataclass
class Error(Exception):
    message: str
    items: Optional[List[str]] = None
    error: Optional[requests.HTTPError] = field(default=None, repr=False)

    def with_error(self, ex: requests.HTTPError) -> Error:
        self.error = ex
        return self

    @classmethod
    def from_dict(cls: Type[T], payload: Dict[str, Any]) -> T:
        message = payload.get("message", "An error occurred.")
        items = payload.get("items") if isinstance(payload.get("items"), list) else None
        return cls(message=message, items=items)

    def __str__(self) -> str:
        return self.message


@dataclass
class BadRequestError(Error):
    """HTTP 400"""
    pass


@dataclass
class UnauthorizedError(Error):
    """HTTP 401"""
    pass


@dataclass
class ForbiddenError(Error):
    """HTTP 403"""
    pass


@dataclass
class NotFoundError(Error):
    """HTTP 404"""
    pass


@dataclass
class InternalServerError(Error):
    """HTTP 5xx"""
    pass


@dataclass
class CodeOceanError(Error):
    """Fallback for unexpected errors"""
    pass
