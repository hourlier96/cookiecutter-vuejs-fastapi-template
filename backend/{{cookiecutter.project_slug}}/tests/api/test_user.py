from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.sqlmodel.models.user import User
from tests.utils.user import create_random_user, get_random_user


DATASOURCES_URL = f"{settings.API_PREFIX}/sql_users"


def test_create_user(client: TestClient, db: Session) -> None:
    user = get_random_user()
    response = client.post(
        DATASOURCES_URL,
        json=jsonable_encoder(user),
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get("email") == user.email
    # Delete user
    db.delete(db.exec(select(User).where(User.id == content.get("id"))).first())
    db.commit()


def test_get_user(client: TestClient, db: Session) -> None:
    user = create_random_user(db)
    response = client.get(
        f"{DATASOURCES_URL}/{user.id}",
    )
    assert response.status_code == 200
    content = response.json()
    assert content.get("id") is not None

    # Delete user
    db.delete(db.exec(select(User).where(User.id == user.id)).first())
    db.commit()


def test_get_users(client: TestClient, db: Session) -> None:
    users = [create_random_user(db), create_random_user(db), create_random_user(db)]
    response = client.get(
        f"{DATASOURCES_URL}",
    )
    assert response.status_code == 200

    content = response.json()
    assert content.get("total") == len(users)
    items = content.get("items")
    assert len(items) == len(users)

    for user in users:
        db.delete(db.exec(select(User).where(User.id == user.id)).first())
        db.commit()
