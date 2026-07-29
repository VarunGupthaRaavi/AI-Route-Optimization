from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Base Pydantic v2 Schema establishing global ORM compatibility and configuration defaults.
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


class ResponseModel(BaseSchema, Generic[T]):
    """
    Standardized API Success Response Envelope for single payload contracts.
    """
    success: bool = Field(default=True, description="Success status flag")
    data: Optional[T] = Field(default=None, description="Response payload object")
    message: str = Field(default="Operation completed successfully.", description="Informational message")
    request_id: Optional[str] = Field(default=None, description="Unique trace identifier")


class PaginatedResponse(BaseSchema, Generic[T]):
    """
    Standardized API Paginated Response Container.
    """
    items: List[T] = Field(default_factory=list, description="List of items for the current page")
    total: int = Field(default=0, description="Total count of matching records in database")
    page: int = Field(default=1, description="Current page index (1-based)")
    page_size: int = Field(default=20, description="Number of items per page")
    total_pages: int = Field(default=0, description="Calculated total pages count")
    has_next: bool = Field(default=False, description="Flag indicating if subsequent page exists")
    has_prev: bool = Field(default=False, description="Flag indicating if prior page exists")


class ErrorDetails(BaseSchema):
    """
    Structured Error Detail payload.
    """
    code: str = Field(..., description="Machine-readable error classification code")
    message: str = Field(..., description="Human-readable error description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Contextual error metadata")
    status_code: int = Field(..., description="HTTP status code")
    request_id: Optional[str] = Field(default=None, description="Unique trace identifier")


class ErrorResponse(BaseSchema):
    """
    Standardized API Error Response Envelope.
    """
    success: bool = Field(default=False, description="Success status flag")
    error: ErrorDetails = Field(..., description="Error detail container")
