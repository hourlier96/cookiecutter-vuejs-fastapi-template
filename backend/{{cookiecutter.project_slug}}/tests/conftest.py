from typing import Generator, Optional

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session

from app.sqlmodel import SQLModel
from app.sqlmodel import engine

fake = Faker()
test_session = None


def get_test_session() -> Optional[Session]:
    return test_session


@pytest.fixture(scope="session")
def session() -> Generator:
    SQLModel.metadata.create_all(engine)

    with Session(engine, autoflush=False, autocommit=False) as s:
        global test_session
        test_session = s
        yield s

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db(session: Session) -> Generator:
    # we use nested session (savepoint) in order to rollback all changes between each tests
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess: Session, transaction) -> None:  # type: ignore
        if transaction.nested and not transaction._parent.nested:
            sess.begin_nested()

    yield session

    try:
        session.rollback()
        event.remove(session, "after_transaction_end", restart_savepoint)
    finally:
        session.close()


@pytest.fixture(scope="session")
def client() -> Generator:
    from app.sqlmodel.api.deps import get_session
    from app.main import app

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as c:
        yield c
