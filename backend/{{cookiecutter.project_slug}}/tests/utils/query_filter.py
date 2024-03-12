import json
from app.core.config import settings

DATASOURCES_URL = f"{settings.API_PREFIX}/sql_users"


async def call_from_operator(client, query_params, field, operator, value):
    query_params["filters"] = json.dumps([{"field": field, "operator": operator, "value": value}])
    response = await client.get(
        DATASOURCES_URL,
        params=query_params,
    )
    assert response.status_code == 200
    return response.json()
