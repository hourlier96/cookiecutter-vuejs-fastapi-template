from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from tests.utils.todo import create_random_todo, build_todo_in
from tests.utils.user import create_random_user

DATASOURCES_URL = f"{settings.API_PREFIX}/sql_todos"


async def test_get_todo(client: AsyncClient, db: AsyncSession) -> None:
    await create_random_todo(db)
    response = await client.get(
        f"{DATASOURCES_URL}/{1}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get("id") == 1


async def test_get_todos(client: AsyncClient, db: AsyncSession) -> None:
    await create_random_todo(db)
    response = await client.get(
        f"{DATASOURCES_URL}",
    )
    assert response.status_code == 200

    content = response.json()
    assert content.get("total") == 1
    items = content.get("items")
    assert len(items) == 1
    assert items[0].get("id") == 1


async def test_create_todo(client: AsyncClient, db: AsyncSession) -> None:
    await create_random_user(db)
    await create_random_user(db)
    todo = build_todo_in()
    response = await client.post(
        DATASOURCES_URL,
        json=jsonable_encoder(todo),
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get("id") is not None


async def test_update_todo(client: AsyncClient, db: AsyncSession) -> None:
    todo = await create_random_todo(db)
    todo.title = "updated"
    response = await client.put(
        f"{DATASOURCES_URL}/{todo.id}",
        json={
            "title": todo.title,
            "description": todo.description,
            "priority": todo.priority,
            "users_id": [],
        },
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get("title") == todo.title


async def test_delete_todo(client: AsyncClient, db: AsyncSession) -> None:
    todo = await create_random_todo(db)
    response = await client.delete(
        f"{DATASOURCES_URL}/{todo.id}",
    )
    assert response.status_code == 200

    response = await client.get(
        f"{DATASOURCES_URL}/{todo.id}",
    )
    assert response.status_code == 404
