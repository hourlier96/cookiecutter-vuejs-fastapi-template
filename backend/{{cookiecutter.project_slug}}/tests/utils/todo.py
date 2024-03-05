import random

from faker import Faker
from sqlmodel import Session

from app.sqlmodel import crud
from app.sqlmodel.models.todo import TodoCreate, TodoPriority, TodoRead

fake = Faker()


def get_random_todo() -> TodoCreate:
    todo_in = TodoCreate(
        title=fake.catch_phrase(),
        description=fake.paragraph(nb_sentences=3),
        priority=random.choice(list(TodoPriority)),
        users_id=[],
    )
    return todo_in


def create_random_todo(db: Session, commit=False) -> TodoRead:
    report_in = get_random_todo()
    report = crud.todos.create(db=db, obj_in=report_in, commit=commit)
    return TodoRead.model_validate(report)
