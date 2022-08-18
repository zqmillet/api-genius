from pytest import mark
from requests import get
from requests import post
from api_genius import Router

@mark.usefixtures('create_tables', 'user_model', 'server')
def test_gen_api() -> None:
    import pdb; pdb.set_trace()
