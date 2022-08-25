from typing import Type
from urllib.parse import quote
from multiprocessing import Process
from time import sleep

from subprocess import Popen
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import create_engine
from pytest import fixture
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest
from _pytest.python import Function
from jsonref import loads

from api_genius import Application

def create_tables(database_engine, models):
    """
    this function is used to
    """
    for model in models:
        model.__table__.create(database_engine, checkfirst=True)

def drop_tables(database_engine, models):
    for model in models:
        model.__table__.drop(database_engine, checkfirst=True)

def pytest_runtest_call(item: Function):
    for mark in item.iter_markers():
        if mark.name == 'create_tables':
            create_tables(item._request.getfixturevalue('database_engine'), *mark.args, **mark.kwargs)

def pytest_runtest_teardown(item: Function):
    for mark in item.iter_markers():
        if mark.name == 'create_tables':
            drop_tables(item._request.getfixturevalue('database_engine'), *mark.args, **mark.kwargs)

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

@fixture(name='database_engine', scope='session')
def _database_engine(mysql_host, mysql_port, mysql_username, mysql_password, mysql_database):
    engine_url = f'mysql+pymysql://{quote(mysql_username)}:{quote(mysql_password)}@{mysql_host}:{mysql_port}'
    engine = create_engine(engine_url)
    with engine.connect() as connection:
        connection.execute(f'create database if not exists {mysql_database}')
        yield create_engine(f'{engine_url}/{mysql_database}')
        connection.execute(f'drop database if exists {mysql_database}')

@fixture(name='application', scope='function')
def _application():
    return Application()

class Client(TestClient):
    @property
    def openapi(self):
        return loads(self.get('/openapi.json').text)

@fixture(name='client', scope='function')
def _client(application):
    return Client(app=application)
