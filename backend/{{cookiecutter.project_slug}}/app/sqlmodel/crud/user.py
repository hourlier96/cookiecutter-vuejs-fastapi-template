from app.sqlmodel.crud.base import CRUDBase
from app.sqlmodel.models.user import User, UserCreate, UserUpdate

users = CRUDBase[User, UserCreate, UserUpdate](User)
