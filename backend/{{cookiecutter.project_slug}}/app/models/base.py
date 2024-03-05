from typing import Generic, List, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


def to_camel(snake_str: str) -> str:
    words = snake_str.split("_")
    return words[0] + "".join(w.title() for w in words[1:])


class DateTimeModelMixin(BaseModel, Generic[T]):
    created_at: T
    updated_at: T

    class ConfigDict:
        alias_generator = to_camel
        populate_by_name = True


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int

    class ConfigDict:
        alias_generator = to_camel
        populate_by_name = True
