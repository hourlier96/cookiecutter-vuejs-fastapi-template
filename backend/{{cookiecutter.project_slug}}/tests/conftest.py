import asyncio
from contextlib import ExitStack

import pytest
import httpx

from app.main import app as actual_app
from app.sqlmodel import SQLModel
from app.sqlmodel.db import DatabaseAsyncSessionManager, get_db_session


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield actual_app


def get_sqlalchemy_database_uri(config):
    """
    Function to get SQLALCHEMY_DATABASE_URI from pytest configuration.
    """
    env_options = config.getini("env")
    for option in env_options:
        if option.startswith("SQLALCHEMY_DATABASE_URI="):
            return option.split("=", 1)[1]
    raise ValueError("SQLALCHEMY_DATABASE_URI not found in pytest configuration")


@pytest.fixture(scope="session")
def session_manager(request):
    return DatabaseAsyncSessionManager(get_sqlalchemy_database_uri(request.config))


@pytest.fixture(scope="function", autouse=True)
async def setup_database(session_manager: DatabaseAsyncSessionManager):
    async with session_manager._engine.begin() as conn:
        asyncio.get_running_loop()
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


@pytest.fixture(scope="function")
async def client():
    async with httpx.AsyncClient(app=actual_app, base_url="http://localhost:8000") as c:
        yield c


@pytest.fixture(scope="function", autouse=True)
async def transactional_session(session_manager: DatabaseAsyncSessionManager):
    async with session_manager.session() as session:
        try:
            await session.begin()
            yield session
        finally:
            await session.rollback()  # Rolls back the outer transaction


@pytest.fixture(scope="function")
async def db(transactional_session):
    yield transactional_session


@pytest.fixture(scope="function", autouse=True)
async def session_override(app, db):
    async def get_db_session_override():
        yield db

    app.dependency_overrides[get_db_session] = get_db_session_override
