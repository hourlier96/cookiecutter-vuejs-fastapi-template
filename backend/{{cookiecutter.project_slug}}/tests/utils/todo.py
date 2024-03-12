import random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.sqlmodel.crud.todo import todos as crud_todo
from app.sqlmodel.models.todo import TodoCreate, TodoPriority, TodoRead

fake = Faker()


def build_todo_in() -> TodoCreate:
    todo_in = TodoCreate(
        title=fake.catch_phrase(),
        description=fake.paragraph(nb_sentences=3),
        priority=random.choice(list(TodoPriority)),
        users_id=[],
    )
    return todo_in


async def create_random_todo(db: AsyncSession) -> TodoRead:
    report_in = build_todo_in()
    report = await crud_todo.create(db=db, obj_in=report_in)
    return TodoRead.model_validate(report)
