from pytest import mark
from requests import get
from requests import post

from api_genius import Router
from action_words import prepare_table
from action_words import User

@prepare_table(model=User)
def test_gen_api(start_server):
    pass
