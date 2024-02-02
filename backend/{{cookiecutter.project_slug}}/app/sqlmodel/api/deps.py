import json
from typing import Generator, List, Optional

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from sqlmodel import Session

from app.sqlmodel import engine
from app.sqlmodel.models.base import QueryFilter

oauth2_scheme = HTTPBearer()


def get_session() -> Generator:
    with Session(engine) as session:
        yield session


def parse_query_filter_params(filters: Optional[str] = None) -> List[QueryFilter]:
    if not filters:
        return []

    query_filters = json.loads(filters)

    if isinstance(query_filters, list):
        return [QueryFilter(**filter_) for filter_ in query_filters]
    elif isinstance(query_filters, dict):
        return [QueryFilter(**query_filters)]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filters",
        )
