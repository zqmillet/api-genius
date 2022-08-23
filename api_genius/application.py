from typing import Dict
from typing import List
from typing import Callable
from typing import Type
from string import Formatter
from dataclasses import dataclass

from fastapi import FastAPI
from fastapi import Depends
from fastapi import Path
from fastapi.params import Path as PathType
from fastapi.params import Depends as DependsType
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.schema import Table
from sqlalchemy.orm import registry
from sqlalchemy.engine.base import Engine

class Base(metaclass=DeclarativeMeta):
    """
    this is the base class of sqlachemy model.
    """
    __abstract__ = True
    __table__: Table
    __tablename__: str
    registry = registry()
    metadata = registry.metadata

def get_parameters(path: str, model: Type[Base], method: str) -> Type[object]:
    """
    this function is used to create parameters type.
    """
    placeholders: List[str] = [placeholder for _, placeholder, _, _ in Formatter().parse(path) if placeholder]

    fields: Dict[str, PathType] = {}
    annotations: Dict[str, type] = {}

    for placeholder in placeholders:
        fields[placeholder] = Path(...)
        annotations[placeholder] = model.__table__.columns[placeholder].type.python_type

    path_parameter_model = type(
        f'path_parameter_model_of_model_{model.__tablename__}_{method}',
        (object,),
        fields
    )
    path_parameter_model.__annotations__ = annotations
    path_parameter_model = dataclass(path_parameter_model)
    return path_parameter_model

class Application(FastAPI):
    """
    inherit the class FastAPI, and provide some methods.
    """
    def add_create_api(self, path: str, database_engine: Engine, method: str = 'post') -> Callable[[Type[Base]], None]:
        """
        this function is used to bind api of creating a resource.
        """
        def _add_create_api(model: Type[Base]) -> None:
            def wapper(path_parameters: DependsType = Depends()) -> None:
                print(path_parameters, database_engine)
            wapper.__annotations__ = {'path_parameters': get_parameters(path, model, method)}

            self.post(path)(wapper)
        return _add_create_api
