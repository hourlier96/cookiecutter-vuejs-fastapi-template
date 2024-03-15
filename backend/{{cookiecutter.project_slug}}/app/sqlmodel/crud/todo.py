from sqlmodel import select
from app.sqlmodel.crud.base import CRUDBase
from app.sqlmodel.models.todo import Todo, TodoCreate, TodoUpdate
from app.sqlmodel.models.user import User
from app.sqlmodel.api.deps import session_dep


class CrudTodo(CRUDBase[Todo, TodoCreate, TodoUpdate]):
    async def update_users(self, db: session_dep, todo_in: TodoCreate, todo: Todo):
        """
        Update many to many relationship if list of users_id specified
        """
        if todo_in.users_id:
            statement = select(User).where(User.id.in_(todo_in.users_id))
            users_list = (await db.scalars(statement)).all()
            todo.users = [u for u in users_list]


todos = CrudTodo(Todo)
