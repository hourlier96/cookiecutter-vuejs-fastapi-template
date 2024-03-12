from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status


from app.sqlmodel.crud.user import users as crud_user
from app.sqlmodel.api.deps import session_dep, parse_query_filter_params
from app.core.cloud_logging import log
from app.core.config import settings
from app.models.base import Page
from app.sqlmodel.models.base import QueryFilter
from app.sqlmodel.models.user import User, UserCreate, UserRead

router = APIRouter()


@router.get(
    "",
    response_model=Page[UserRead],
)
async def read_users(
    *,
    db: session_dep,
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE),
    sort: Optional[str] = None,
    filters: List[QueryFilter] = Depends(parse_query_filter_params),
    is_desc: bool = False,
) -> Page[User]:
    """
    Retrieve user.
    """
    users = await crud_user.get_multi(
        db, skip=skip, limit=limit, sort=sort, is_desc=is_desc, filters=filters
    )
    return users


@router.post(
    "",
    response_model=UserRead,
)
async def create_user(
    *,
    db: session_dep,
    user_in: UserCreate,
) -> User:
    """
    Create new user.
    """
    try:
        user = await crud_user.create(db=db, obj_in=user_in)
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user"
        )
    return user


@router.get(
    "/{_id}",
    response_model=UserRead,
)
async def read_user(
    *,
    db: session_dep,
    _id: int,
) -> Any:
    """
    Get user by ID
    """
    user = await crud_user.get(db=db, id=_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
