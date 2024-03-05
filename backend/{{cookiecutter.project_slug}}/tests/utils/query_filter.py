import json
from app.core.config import settings

DATASOURCES_URL = f"{settings.API_PREFIX}/sql_users"


def call_from_operator(client, query_params, field, operator, value):
    query_params["filters"] = json.dumps([{"field": field, "operator": operator, "value": value}])
    response = client.get(
        DATASOURCES_URL,
        params=query_params,
    )
    assert response.status_code == 200
    return response.json()
