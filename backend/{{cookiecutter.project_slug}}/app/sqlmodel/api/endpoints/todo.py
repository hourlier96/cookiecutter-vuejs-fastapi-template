from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.sqlmodel import crud
from app.sqlmodel.api.deps import get_session, parse_query_filter_params
from app.core.cloud_logging import log
from app.core.config import settings
from app.models.base import Page
from app.sqlmodel.models.base import QueryFilter
from app.sqlmodel.models.todo import Todo, TodoCreate, TodoRead, TodoReadUsers, TodoUpdate
from app.sqlmodel.models.user import User

router = APIRouter()


@router.get(
    "",
    response_model=Page[TodoRead],
)
def read_todos(
    *,
    db: Session = Depends(get_session),
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE),
    sort: Optional[str] = None,
    filters: List[QueryFilter] = Depends(parse_query_filter_params),
    is_desc: bool = False,
) -> Page[Todo]:
    """
    Retrieve todos.
    """
    try:
        todos = crud.todos.get_multi(
            db, skip=skip, limit=limit, sort=sort, is_desc=is_desc, filters=filters
        )
        return todos
    except (AttributeError, KeyError, ValueError) as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )


@router.get(
    "/withusers",
    response_model=List[TodoReadUsers],
)
def read_todos_users(
    *,
    db: Session = Depends(get_session),
    skip: Optional[int] = Query(0, ge=0),
    limit: Optional[int] = Query(None, ge=1, le=settings.MAX_PAGE_SIZE),
    sort: Optional[str] = None,
    is_desc: bool = False,
) -> List[Todo]:
    """
    Retrieve todos sorted by users.
    """
    todos = crud.todos.get_multi(db, skip=skip, limit=limit, sort=sort, is_desc=is_desc)
    return todos.items


@router.post(
    "",
    response_model=TodoRead,
)
def create_todo(
    *,
    db: Session = Depends(get_session),
    todo_in: TodoCreate,
) -> Any:
    """
    Create a todo.
    """
    try:
        todo = crud.todos.create(db=db, obj_in=todo_in, commit=False)
        if todo_in.users_id:
            users_list = db.exec(select(User).where(User.id.in_(todo_in.users_id))).all()
            todo.users = [u for u in users_list]
    except Exception as e:
        db.rollback()
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create todo"
        )
    else:
        db.commit()
        db.refresh(todo)
    return todo


@router.put(
    "/{_id}",
    response_model=TodoRead,
)
def update_todo(
    *,
    db: Session = Depends(get_session),
    _id: int,
    todo_in: TodoUpdate,
) -> Any:
    """
    Update a todo.
    """
    todo = crud.todos.get(db=db, id=_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    try:
        todo = crud.todos.update(db=db, db_obj=todo, obj_in=todo_in)
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update todo"
        )
    return todo


@router.get(
    "/{_id}",
    response_model=TodoRead,
)
def read_todo(
    *,
    db: Session = Depends(get_session),
    _id: int,
) -> Any:
    """
    Get todo by ID.
    """
    todo = crud.todos.get(db=db, id=_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get(
    "/{_id}/users/",
    response_model=TodoReadUsers,
)
def read_todo_users(
    *,
    db: Session = Depends(get_session),
    _id: int,
) -> Todo:
    """
    Get user linked to a todo by todo ID.
    """
    todo = crud.todos.get(db=db, id=_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.delete(
    "/{_id}",
    response_model=TodoRead,
)
def delete_todo(
    *,
    db: Session = Depends(get_session),
    _id: int,
) -> Any:
    """
    Delete a todo.
    """
    todo = crud.todos.get(db=db, id=_id)
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    try:
        todo = crud.todos.remove(db=db, id=_id)
    except Exception as e:
        log.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete todo"
        )

    return todo
