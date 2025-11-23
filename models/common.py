from typing import Generic, TypeVar, List, Optional
from sqlmodel import SQLModel


T = TypeVar("T")


class Pagination(SQLModel, Generic[T]):
    result: List[T]
    next_cursor: Optional[str] = None
    has_next: bool
    size: int
