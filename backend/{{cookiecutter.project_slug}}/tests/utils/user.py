import random
from faker import Faker
from app.sqlmodel.models.user import UserCreate, UserRead
from sqlmodel import Session
from app.sqlmodel import crud

fake = Faker()


def get_random_user() -> UserCreate:
    user_in = UserCreate(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        is_admin=fake.pybool(),
        login_times=random.randint(0, 1000) if random.random() < 0.5 else None,
    )
    return user_in


def create_random_user(db: Session) -> UserRead:
    user_in = get_random_user()
    user = crud.users.create(db=db, obj_in=user_in)
    return UserRead.model_validate(user)


# - - -


def get_user(
    first_name: str, last_name: str, email: str, is_admin: bool, login_times: int | None
) -> UserCreate:
    user_in = UserCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        is_admin=is_admin,
        login_times=login_times,
    )
    return user_in


def create_user(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    is_admin: bool,
    login_times: int | None,
) -> UserRead:
    user_in = get_user(first_name, last_name, email, is_admin, login_times)
    user = crud.users.create(db=db, obj_in=user_in)
    return UserRead.model_validate(user)
