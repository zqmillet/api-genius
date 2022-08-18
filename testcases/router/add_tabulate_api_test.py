from pytest import mark
from requests import get
from api_genius import Router

@mark.usefixtures('create_tables', 'user_model')
def test_add_tabulate_api_test() -> None:
    pass
