from pytest import fixture
from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest

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
