from pydantic import BaseModel
from typing import Generic, List, TypeVar

T = TypeVar("T")

def to_camel(snake_str: str) -> str:
    words = snake_str.split("_")
    return words[0] + "".join(w.title() for w in words[1:])


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int

    class Config:
        alias_generator = to_camel
        populate_by_name = True
