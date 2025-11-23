"""Pagination utilities for API endpoints."""
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.orm import Query


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    page: int = 1
    page_size: int = 20

    class Config:
        from_attributes = True

    def validate_params(self) -> None:
        """Validate pagination parameters."""
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 20
        if self.page_size > 100:
            self.page_size = 100  # Max 100 items per page


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True


def paginate(query: Query, page: int = 1, page_size: int = 20) -> tuple[List, int]:
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy Query object
        page: Page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Tuple of (items, total_count)
    """
    # Validate params
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100

    # Get total count
    total = query.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Get paginated items
    items = query.limit(page_size).offset(offset).all()

    return items, total


def create_paginated_response(
    items: List[T],
    total: int,
    page: int,
    page_size: int
) -> PaginatedResponse[T]:
    """
    Create a paginated response object.

    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Items per page

    Returns:
        PaginatedResponse object
    """
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )
