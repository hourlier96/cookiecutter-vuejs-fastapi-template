import json
from typing import Annotated, List, Optional
from fastapi import HTTPException, status, Depends
from app.api.deps import raise_400
from app.sqlmodel.models.base import QueryFilter
from app.sqlmodel.db import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

session_dep = Annotated[AsyncSession, Depends(get_db_session)]


def parse_query_filter_params(filters: Optional[str] = None) -> List[QueryFilter]:
    if not filters:
        return []

    query_filters = json.loads(filters)

    if isinstance(query_filters, list):
        return [QueryFilter(**filter_) for filter_ in query_filters]
    elif isinstance(query_filters, dict):
        return [QueryFilter(**query_filters)]
    else:
        raise_400(msg='Invalid query filters')
