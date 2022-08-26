from typing import Dict
from typing import List
from typing import Callable
from typing import Type
from typing import Tuple
from typing import Any
from typing import Optional
from string import Formatter
from uuid import uuid4
from dataclasses import dataclass
from numbers import Real
from functools import lru_cache

from fastapi import FastAPI
from fastapi import Depends
from fastapi import Path
from fastapi.params import Path as PathType
from fastapi.params import Depends as DependsType
from pydantic import create_model
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic import BaseModel
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.schema import Table
from sqlalchemy.orm import registry
from sqlalchemy.engine.base import Engine
from sqlalchemy import Column as _Column
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String


class Base(metaclass=DeclarativeMeta):
    """
    this is the base class of sqlachemy model.
    """
    __abstract__ = True
    __table__: Table
    __tablename__: str

    registry = registry()
    metadata = registry.metadata

class Column(_Column):
    """
    this class is subclass of class Column from sqlachemy module.
    it provides some extension features.
    """
    def __init__(self,
        *args,
        example: Optional[Any] = None,
        private: bool = False,
        ge: Optional[Real] = None,
        gt: Optional[Real] = None,
        le: Optional[Real] = None,
        lt: Optional[Real] = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.example = example
        self.private = private
        self.ge = ge
        self.le = le
        self.gt = gt
        self.lt = lt

def _get_auto_generated_class_name(model: Type[Base]) -> str:
    return f'{model.__tablename__}_{str(uuid4())[:8]}'

def _get_path_parameters(path: str, model: Type[Base], method: str) -> Type[object]:
    """
    this function is used to create path parameters type.
    """
    placeholders: List[str] = [placeholder for _, placeholder, _, _ in Formatter().parse(path) if placeholder]
    path_fields: Dict[str, PathType] = {}
    path_annotations: Dict[str, type] = {}

    for placeholder in placeholders:
        if placeholder not in model.__table__.columns:
            continue

        column: Column = model.__table__.columns[placeholder]
        path_fields[placeholder] = Path(..., title=column.comment, example=_get_example_value(column), **_get_validations(column))
        path_annotations[placeholder] = column.type.python_type

    path_parameter_model = type(_get_auto_generated_class_name(model), (object,), path_fields)
    path_parameter_model.__annotations__ = path_annotations
    path_parameter_model = dataclass(path_parameter_model)
    return path_parameter_model

def _get_example_value(column: _Column) -> Optional[Any]:
    """
    this function is used to get example value from column.
    """
    if isinstance(column, Column):
        return column.example
    return None

def _get_default_value(column: _Column) -> Optional[Any]:
    """
    this function is used to get default value from column.
    """
    if column.default is None:
        if column.nullable:
            return None
        return ...
    return column.default.arg

def _get_validations(column: _Column) -> Dict[str, Any]:
    validations: Dict[str, Any] = {}
    if isinstance(column.type, (Integer, Float)):
        validations.update({'gt': column.gt, 'lt': column.lt, 'ge': column.ge, 'le': column.le})
    elif isinstance(column.type, Enum):
        pass
    elif isinstance(column.type, String):
        validations.update({'max_length': column.type.length})
    return validations

def _get_python_type(column: _Column) -> type:
    return column.type.python_type

def _get_body_parameters(path: str, model: Type[Base], method: str) -> Type[object]:
    """
    this function is used to create body parameters type.
    """
    placeholders: List[str] = [placeholder for _, placeholder, _, _ in Formatter().parse(path) if placeholder]
    body_fields: Dict[str, Any] = {} # type: ignore

    for name, column in model.__table__.columns.items():
        if name in placeholders:
            continue

        if column.private:
            continue

        body_fields[name] = (
            _get_python_type(column),
            Field(
                title=column.comment,
                example=_get_example_value(column),
                default=_get_default_value(column),
                **_get_validations(column)
            )
        )

    return create_model(_get_auto_generated_class_name(model), **body_fields)

@lru_cache
def _sqlalchemy_model_to_pydantic_model(model: Type[Base]):
    fields: Dict[str, FieldInfo] = {}

    for name, column in model.__table__.columns.items():
        fields[name] = (
            column.type.python_type,
            Field(default=_get_default_value(column), title=column.comment)
        )

    return create_model(model_name_prefix + model.__name__, __config__=config, **fields)

def _get_response_model(model):
    pass

def _get_api_path(model: Type[Base]) -> str:
    items = ['', model.__tablename__]
    for column in model.__table__.columns:
        if not column.primary_key:
            continue
        items += [f'{{{column.name}}}']
    return '/'.join(items)

class Application(FastAPI):
    """
    inherit the class FastAPI, and provide some methods.
    """
    def add_create_api(self, database_engine: Engine, path: Optional[str] = None, method: str = 'post') -> Callable[[Type[Base]], None]:
        """
        this function is used to bind api of creating a resource.
        """
        def _add_create_api(model: Type[Base]) -> Type[Base]:
            api_path = path or _get_api_path(model)

            def wrapper(body_parameters: BaseModel, path_parameters: DependsType = Depends()) -> None:
                print(path_parameters, body_parameters, database_engine)

            wrapper.__annotations__ = {
                'path_parameters': _get_path_parameters(api_path, model, method),
                'body_parameters': _get_body_parameters(api_path, model, method),
            }

            self.post(api_path, summary=f'create {model.__tablename__}')(wrapper)
            return model
        return _add_create_api

    def add_read_api(self, database_engine: Engine, path: Optional[str] = None, method: str = 'get'):
        """
        this function is used to bind api of reading a resource.
        """
        def _add_read_api(model: Type[Base]) -> Type[Base]:
            api_path = path or _get_api_path(model)

            def wrapper(path_parameters: DependsType = Depends()) -> None:
                print(path_parameters, database_engine)

            wrapper.__annotations__ = {
                'path_parameters': _get_path_parameters(api_path, model, method)
            }

            self.get(api_path, summary=f'create {model.__tablename__}')(wrapper)
            return model
        return _add_read_api
