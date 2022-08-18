import builtins
from typing import Type
from typing import TypeVar
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from urllib.parse import quote
from multiprocessing import Process
from time import sleep

from uvicorn import run
from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import create_engine
from pytest import fixture
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest

from api_genius import Router
from action_words import set_trace

import pytest

def is_open_port(port: int) -> bool:
    with socket(AF_INET, SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0

def pytest_addoption(parser: Parser):
    parser.addoption(
        '--mysql-host',
        type=str,
        action='store',
        default='host.docker.internal',
        help='specify the host of mysql for test'
    )

    parser.addoption(
        '--mysql-port',
        type=int,
        action='store',
        default=3306,
        help='specify the port of mysql for test'
    )

    parser.addoption(
        '--mysql-username',
        type=str,
        action='store',
        default='root',
        help='specify the username of mysql for test'
    )

    parser.addoption(
        '--mysql-password',
        type=str,
        action='store',
        default='root',
        help='specify the password of mysql for test'
    )

    parser.addoption(
        '--mysql-database',
        type=str,
        action='store',
        default='kinopico',
        help='specify the database name of mysql for test'
    )

    parser.addoption(
        '--server-port',
        type=int,
        action='store',
        default=1926,
        help='specify the port of the server under test'
    )

@fixture(name='mysql_host', scope='session')
def _mysql_host(request: SubRequest) -> str:
    return request.config.getoption('mysql_host')

@fixture(name='mysql_port', scope='session')
def _mysql_port(request: SubRequest) -> int:
    return request.config.getoption('mysql_port')

@fixture(name='mysql_username', scope='session')
def _mysql_username(request: SubRequest) -> str:
    return request.config.getoption('mysql_username')

@fixture(name='mysql_password', scope='session')
def _mysql_password(request: SubRequest) -> str:
    return request.config.getoption('mysql_password')

@fixture(name='mysql_database', scope='session')
def _mysql_database(request: SubRequest) -> str:
    return request.config.getoption('mysql_database')

@fixture(name='server_port', scope='session')
def _server_port(request: SubRequest) -> int:
    return request.config.getoption('server_port')

@fixture(name='base_class', scope='session')
def _base_class() -> Type[DeclarativeMeta]:
    return declarative_base()

Base = TypeVar('Base')

@fixture(name='patch_breakpoint', scope='session')
def _patch_breakpoint():
    origin_breakpoint = builtins.breakpoint
    builtins.breakpoint = set_trace
    yield
    builtins.breakpoint = origin_breakpoint

@fixture(name='user_model', scope='session')
def _user_model(base_class: Type[Base]) -> Type[Base]:
    class User(base_class): # type: ignore
        __tablename__ = 'users'

        id = Column(String(50), primary_key=True)
        name = Column(String(50))
        age = Column(Integer())
    return User

@fixture(name='database_engine', scope='session')
def _database_engine(mysql_host, mysql_port, mysql_username, mysql_password, mysql_database):
    engine_url = f'mysql+pymysql://{quote(mysql_username)}:{quote(mysql_password)}@{mysql_host}:{mysql_port}'
    engine = create_engine(engine_url)
    with engine.connect() as connection:
        connection.execute(f'create database if not exists {mysql_database}')
        yield create_engine(f'{engine_url}/{mysql_database}')
        connection.execute(f'drop database if exists {mysql_database}')

@fixture(name='used_models', scope='function')
def _used_models(request: SubRequest, base_class):
    models = []
    for fixture_name in request.fixturenames:
        try:
            fixture_value = request.getfixturevalue(fixture_name)
        except LookupError:
            continue

        if not isinstance(fixture_value, type):
            continue

        if fixture_value is base_class:
            continue

        if not issubclass(fixture_value, base_class):
            continue

        models.append(fixture_value)
    return models

@fixture(name='create_tables', scope='function')
def _create_tables(used_models, base_class, database_engine):
    for model in used_models:
        model.__table__.create(database_engine)
    yield
    for model in used_models:
        model.__table__.drop(database_engine)

@fixture(name='server', scope='function')
def _server(user_model: Type[Base], server_port: int, patch_breakpoint) -> None:
    assert not is_open_port(server_port)

    application = FastAPI()
    router = Router()
    router.add_tabulate_api(None, user_model)
    application.include_router(router)

    process = Process(target=run, args=(application,), kwargs={'port': server_port, 'log_level': 'critical'}, daemon=True)
    process.start()

    while not is_open_port(server_port):
        sleep(0.5)
    yield
    process.terminate()


