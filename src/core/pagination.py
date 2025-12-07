import math
from typing import Annotated, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        return self.size


def get_pagination_params(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


Pagination = Annotated[PaginationParams, get_pagination_params]


class PaginatedResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

    model_config = {"arbitrary_types_allowed": True}


async def paginate(
    db: AsyncSession,
    query: Select[tuple[T]],
    params: PaginationParams,
) -> PaginatedResult[T]:
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    paginated_query = query.offset(params.offset).limit(params.limit)
    result = await db.execute(paginated_query)
    items = list(result.scalars().all())

    pages = math.ceil(total / params.size) if params.size > 0 else 0

    return PaginatedResult(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        pages=pages,
    )
