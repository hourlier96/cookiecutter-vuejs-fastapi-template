from sqlmodel import create_engine

from app.core.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# Import all the tables, so that Base has them before being
# imported by Alembic
from sqlmodel import SQLModel  # noqa

from app.sqlmodel.models.todo import Todo  # noqa
from app.sqlmodel.models.user import User  # noqa
from app.sqlmodel.models.userTodo import UserTodo  # noqa
