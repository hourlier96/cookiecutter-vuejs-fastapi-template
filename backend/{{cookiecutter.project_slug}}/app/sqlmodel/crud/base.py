from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select
from sqlmodel import SQLModel, select

from app.models.base import Page
from app.sqlmodel.models.base import QueryFilter, TableBase, to_snake

ModelType = TypeVar("ModelType", bound=TableBase)
CreateModelType = TypeVar("CreateModelType", bound=SQLModel)
UpdateModelType = TypeVar("UpdateModelType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateModelType, UpdateModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLModel class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        statement = select(self.model).where(self.model.id == id)
        return (await db.scalars(statement)).first()

    def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        filters: Optional[List[QueryFilter]] = [],
        is_desc: bool = False,
    ) -> Page[ModelType]:
        statement = select(self.model)
        if filters:
            statement = self.update_query_with_filters_(statement, filters)

        return self.order_and_paginate_results(
            statement, db, skip=skip, limit=limit, sort=sort, is_desc=is_desc
        )

    async def create(
        self, db: AsyncSession, *, obj_in: CreateModelType, commit: bool = True
    ) -> ModelType:
        db_obj = self.model.model_validate(obj_in)
        db.add(db_obj)
        if commit:
            await db.commit()  # to move out of function?
            await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateModelType, Dict[str, Any]],
        commit: bool = True,
    ) -> ModelType:

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        for field in update_data:
            snake_field = to_snake(field)
            if snake_field in update_data:
                # Lists must be managed manually
                if isinstance(update_data[snake_field], list):
                    continue
                setattr(db_obj, snake_field, update_data[snake_field])

        db.add(db_obj)
        if commit:
            await db.commit()  # to move out of function?
            await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, db_obj: ModelType, commit: bool = True) -> str:
        await db.delete(db_obj)
        if commit:
            await db.commit()
        return db_obj

    async def order_and_paginate_results(
        self,
        statement: Select,
        db: AsyncSession,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        is_desc: bool = False,
    ) -> Page[ModelType]:
        if sort:
            sort = to_snake(sort)
            try:
                sort_field = getattr(self.model, sort)
                order_by = desc(sort_field) if is_desc else asc(sort_field)
                statement = statement.order_by(order_by)
            except AttributeError:
                pass

        if skip is not None:
            statement = statement.offset(skip)

        if limit is not None:
            statement = statement.limit(limit)

        items = (await db.scalars(statement)).all()
        total = len(items)
        return Page(items=items, total=total)

    def update_query_with_filters_(
        self, statement: Select, query_filters: List[QueryFilter]
    ) -> Select:
        operator_matcher = {
            "alchemy_func": {
                "=": "__eq__",
                "!=": "__ne__",
                ">": "__gt__",
                "<": "__lt__",
                ">=": "__ge__",
                "<=": "__le__",
                ":": "like",
                "in": "in_",
                "not_in": "notin_",
                "is_null": "is_",
                "is_not_null": "is_not",
            },
            "built_in": {
                "is_empty": '== ""',
                "is_not_empty": '!= ""',
                "is_true": "== True",
                "is_false": "== False",
            },
        }
        for query_filter in query_filters:
            statement = self.manage_operators(statement, query_filter, operator_matcher)

        return statement

    def manage_operators(
        self, statement: Select, query_filter: QueryFilter, operator_matcher: dict
    ) -> Select:
        attribute = getattr(self.model, query_filter.field)
        if not attribute:
            raise AttributeError(f"{self.model.__name__} has no attribute {query_filter.field}")
        if query_filter.operator in operator_matcher["alchemy_func"]:
            operator_value = operator_matcher["alchemy_func"][query_filter.operator]
            column_operator = getattr(attribute, operator_value)
            statement = statement.where(column_operator(query_filter.value))
        elif query_filter.operator in operator_matcher["built_in"]:
            operator_value = operator_matcher["built_in"][query_filter.operator]
            statement = statement.where(
                eval(f"{attribute} {operator_value}", {self.model.__name__: self.model})
            )
        else:
            raise ValueError(f"Operator {query_filter.operator} is not supported")

        return statement
