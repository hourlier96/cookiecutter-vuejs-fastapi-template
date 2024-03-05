import enum
from typing import List, Optional

from sqlmodel import Relationship

from app.sqlmodel.models.base import AppBase, ReadBase, TableBase
from app.sqlmodel.models.userTodo import UserTodo

from app.sqlmodel.models.user import User, UserRead


class TodoPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TodoBase(AppBase):
    title: str
    description: Optional[str]
    priority: TodoPriority


class Todo(TodoBase, TableBase, table=True):
    users: List["User"] = Relationship(back_populates="todos", link_model=UserTodo)


class TodoRead(ReadBase, TodoBase):
    id: int


class TodoReadUsers(AppBase):
    id: int
    users: List["UserRead"] = []


class TodoCreate(TodoBase):
    users_id: Optional[List[int]]


class TodoUpdate(TodoBase):
    users: List["User"] = []
