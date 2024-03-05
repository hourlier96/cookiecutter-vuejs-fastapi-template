import json
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from app.sqlmodel.models.user import User
from tests.utils.query_filter import call_from_operator
from tests.utils.user import create_user
from app.core.config import settings

DATASOURCES_URL = f"{settings.API_PREFIX}/sql_users"


def test_query_filter_users(client: TestClient, db: Session) -> None:
    user0 = create_user(db, "Jean", "jean.dupont@gmail.com", "jean.dupont@gmail.com", True, 135)
    user1 = create_user(db, "Louis", "Ferrand", "louis.ferrand@gmail.com", False, 10)  # noqa
    user2 = create_user(db, "Anna", "", "anna.delcourt@gmail.com", False, None)  # noqa  # noqa

    query_params = {
        "skip": 0,
        # "limit": None,
        "sort": None,
        "is_desc": False,
        "filters": None,
    }
    # Test equality operators
    data = call_from_operator(client, query_params, "first_name", "eq", user0.first_name)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "first_name", "=", user0.first_name)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "email", "!=", user0.email)
    assert data.get("total") > 1
    data = call_from_operator(client, query_params, "email", "ne", user0.email)
    assert data.get("total") > 1
    data = call_from_operator(client, query_params, "email", "neq", user0.email)
    assert data.get("total") > 1
    # Test inclusion operators
    data = call_from_operator(client, query_params, "email", ":", "%dupont%")
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "email", "has", "%dupont%")
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "email", "contains", "%dupont%")
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "email", "includes", "%dupont%")
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "email", "like", "%dupont%")
    assert data.get("total") == 1
    # Test comparison operators
    data = call_from_operator(client, query_params, "login_times", "<", 12)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "lt", 10)
    assert data.get("total") == 0
    data = call_from_operator(client, query_params, "login_times", "<=", 10)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "le", 10)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", ">", 120)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "gt", 135)
    assert data.get("total") == 0
    data = call_from_operator(client, query_params, "login_times", ">=", 135)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "ge", 135)
    assert data.get("total") == 1
    # Test range operators
    data = call_from_operator(client, query_params, "login_times", "in", [1, 5, 10, 100])
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "not_in", [1, 2, 3])
    assert data.get("total") == 2
    # Test type operators
    data = call_from_operator(client, query_params, "login_times", "is_null", None)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "login_times", "is_not_null", None)
    assert data.get("total") == 2
    data = call_from_operator(client, query_params, "last_name", "is_empty", None)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "last_name", "is_not_empty", None)
    assert data.get("total") == 2
    data = call_from_operator(client, query_params, "is_admin", "is_true", None)
    assert data.get("total") == 1
    data = call_from_operator(client, query_params, "is_admin", "is_false", None)
    assert data.get("total") == 2

    # Test sort key
    query_params["sort"] = "first_name"
    data = call_from_operator(client, query_params, "first_name", "is_not_empty", None)
    assert data.get("total") == 3
    items = data.get("items")
    assert items[0].get("first_name") == "Anna"
    assert items[1].get("first_name") == "Jean"
    assert items[2].get("first_name") == "Louis"
    # Test is_desc
    query_params["is_desc"] = True
    data = call_from_operator(client, query_params, "first_name", "is_not_empty", None)
    assert data.get("total") == 3
    items = data.get("items")
    assert items[0].get("first_name") == "Louis"
    assert items[1].get("first_name") == "Jean"
    assert items[2].get("first_name") == "Anna"
    # Test limit
    query_params["limit"] = 1
    data = call_from_operator(client, query_params, "first_name", "is_not_empty", None)
    # Should be 3, but limit is set
    assert data.get("total") == 1

    # Delete used users
    users = [
        db.exec(select(User).where(User.id == user0.id)).first(),
        db.exec(select(User).where(User.id == user1.id)).first(),
        db.exec(select(User).where(User.id == user2.id)).first(),
    ]
    for user in users:
        db.delete(user)
        db.commit()
