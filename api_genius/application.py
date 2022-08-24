from typing import Dict
from typing import List
from typing import Callable
from typing import Type
from typing import Tuple
from typing import Any
from string import Formatter
from dataclasses import dataclass

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
from sqlalchemy import Column

class Base(metaclass=DeclarativeMeta):
    """
    this is the base class of sqlachemy model.
    """
    __abstract__ = True
    __table__: Table
    __tablename__: str

    registry = registry()
    metadata = registry.metadata

def get_path_parameters(path: str, model: Type[Base], method: str) -> Type[object]:
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
        path_fields[placeholder] = Path(..., title=column.comment)
        path_annotations[placeholder] = column.type.python_type

    path_parameter_model = type(
        f'path_parameter_model_of_model_{model.__tablename__}_{method}',
        (object,),
        path_fields
    )
    path_parameter_model.__annotations__ = path_annotations
    path_parameter_model = dataclass(path_parameter_model)
    return path_parameter_model

def get_body_parameters(path: str, model: Type[Base], method: str) -> Type[object]:
    """
    this function is used to create body parameters type.
    """
    placeholders: List[str] = [placeholder for _, placeholder, _, _ in Formatter().parse(path) if placeholder]
    body_fields: Dict[str, Any] = {} # type: ignore

    for name, column in model.__table__.columns.items():
        if name in placeholders:
            continue

        body_fields[name] = (column.type.python_type, Field())

    return create_model(f'path_parameter_model_of_model_{model.__tablename__}_{method}', **body_fields)

class Application(FastAPI):
    """
    inherit the class FastAPI, and provide some methods.
    """
    def add_create_api(self, path: str, database_engine: Engine, method: str = 'post') -> Callable[[Type[Base]], None]:
        """
        this function is used to bind api of creating a resource.
        """
        def _add_create_api(model: Type[Base]) -> None:
            def wapper(body_parameters: BaseModel, path_parameters: DependsType = Depends()) -> None:
                print(path_parameters, body_parameters, database_engine)

            wapper.__annotations__ = {
                'path_parameters': get_path_parameters(path, model, method),
                'body_parameters': get_body_parameters(path, model, method),
            }

            self.post(path, summary=f'create {model.__tablename__}')(wapper)
        return _add_create_api
