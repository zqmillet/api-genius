from requests import get
from api_genius import Router

def test_add_tabulate_api_test(mysql_host: str, mysql_port: int, mysql_username: str, mysql_password: str, server, user_model, server_port) -> None:
    print(get(f'http://localhost:{server_port}/').text)
