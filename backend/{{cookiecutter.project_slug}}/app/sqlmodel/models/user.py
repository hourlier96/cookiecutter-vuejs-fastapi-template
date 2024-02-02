from typing import TYPE_CHECKING, List
from pydantic import ConfigDict

from sqlmodel import Relationship

from app.sqlmodel.models.base import AppBase, ReadBase, TableBase
from app.sqlmodel.models.userTodo import UserTodo

if TYPE_CHECKING:
    from app.sqlmodel.models.todo import Todo, TodoRead


class UserBase(AppBase):
    """User Model"""

    first_name: str
    last_name: str
    email: str


class User(UserBase, TableBase, table=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    todos: List["Todo"] = Relationship(back_populates="users", link_model=UserTodo)


class UserRead(ReadBase, UserBase):
    id: int


class UserReadTopics(ReadBase, UserBase):
    todos: List["TodoRead"] = []


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass
