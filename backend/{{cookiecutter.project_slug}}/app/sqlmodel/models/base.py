import re
from datetime import date, datetime, timezone
from typing import Dict, List, Literal, Optional, Set, TypeVar, Union

from sqlalchemy import TIMESTAMP, text

from fastapi import HTTPException, status
from pydantic import model_validator
from sqlmodel import Column, DateTime, Field, SQLModel

from app.models.base import to_camel

T = TypeVar("T")


def to_snake(camel_str: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def convert_datetime_to_realworld(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class AppBase(SQLModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        json_encoders = {datetime: convert_datetime_to_realworld}


class ReadBase(SQLModel):
    id: int
    created_at: datetime
    updated_at: datetime


class TableBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

    created_at: Optional[datetime] = Field(
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
        default=datetime.now(),
        nullable=False,
    )

    updated_at: Optional[datetime] = Field(
        sa_type=TIMESTAMP(timezone=True),
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP"),
        },
        default=datetime.now(),
        nullable=False,
    )


class QueryFilter(SQLModel):
    # fmt:off
    field: str
    operator: Literal[
        # comparison operators
        "<", "lt",
        "<=", "le",
        ">=", "ge",
        ">", "gt",
        ":", "has", "contains", "includes", "like",
        "=", "eq",
        "!=", "ne", "neq",
        # range operators
        "in",
        "not_in",
        # type operators
        "is_null",
        "is_not_null",
        "is_empty",
        "is_not_empty",
        "is_true",
        "is_false",
    ]
    value: Union[int, date, datetime, str, List, None]
    # fmt:on

    @model_validator(mode="before")
    def validate_value(cls, values: Dict[str, str]) -> dict:
        # fmt:off
        comparison_operators: Set[str] = {
            "<", "lt",
            "<=", "le",
            ">=", "ge",
            ">", "gt",
        }
        range_operators: Set[str] = {
            "in",
            "not_in",
        }
        type_operators: Set[str] = {
            "is_null",
            "is_not_null",
            "is_empty",
            "is_not_empty",
            "is_true",
            "is_false"
        }
        # fmt:on
        special_operators: Set[str] = {*range_operators, *type_operators}

        field, operator, value = values["field"], values.get("operator"), values.get("value")
        values["field"] = to_snake(field)

        if operator not in special_operators:
            if operator in ["eq", "="]:
                values["operator"] = "="
            elif operator in ["ne", "neq", "!="]:
                values["operator"] = "!="
            elif operator in ["has", "contains", "includes", "like", ":"]:
                values["operator"] = ":"
            elif operator in ["gt", ">"]:
                values["operator"] = ">"
            elif operator in ["ge", ">="]:
                values["operator"] = ">="
            elif operator in ["lt", "<"]:
                values["operator"] = "<"
            elif operator in ["le", "<="]:
                values["operator"] = "<="
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid operator",
                )

            if not value:
                raise HTTPException(status_code=400, detail="Value is required for this operator.")

            if not isinstance(value, (int, date, datetime)):
                if operator in comparison_operators:
                    raise ValueError("Some error")
        else:
            if operator in range_operators:
                if not isinstance(value, list):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Value must be a list",
                    )
                if not value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Value cannot be empty",
                    )
            elif operator in type_operators:
                if value:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Value must be empty",
                    )

        return values
