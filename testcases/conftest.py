from typing import Type
from typing import TypeVar
from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM
from multiprocessing import Process
from time import sleep

from uvicorn import run
from fastapi import FastAPI
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from pytest import fixture
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest

from api_genius import Router

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

@fixture(name='user_model', scope='session')
def _user_model(base_class: Type[Base]) -> Type[Base]:
    class User(base_class): # type: ignore
        __tablename__ = 'users'

        id = Column(String(), primary_key=True)
        name = Column(String())
        age = Column(Integer())
    return User

@fixture(name='server', scope='function')
def _server(user_model: Type[Base], server_port: int) -> None:
    assert not is_open_port(server_port)

    application = FastAPI()
    router = Router()
    router.add_tabulate_api(None, user_model)
    application.include_router(router)

    process = Process(target=run, args=(application,), kwargs={'host': '0.0.0.0', 'port': server_port, 'debug': True}, daemon=True)
    process.start()

    while not is_open_port(server_port):
        sleep(0.5)

    yield

    process.terminate()
