from app.sqlmodel.crud.base import CRUDBase
from app.sqlmodel.models.todo import Todo, TodoCreate, TodoUpdate
from app.sqlmodel.models.user import User, UserCreate, UserUpdate

todos = CRUDBase[Todo, TodoCreate, TodoUpdate](Todo)
users = CRUDBase[User, UserCreate, UserUpdate](User)
