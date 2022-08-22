from pytest import mark
from requests import get
from requests import post
from fastapi import FastAPI

from api_genius import Router
from action_words import start_server
from action_words import User

@mark.create_tables(models=[User])
def test_gen_api(server_port, session_maker):
    application = FastAPI()
    router = Router()
    router.add_tabulate_api(path='/', session_class=session_maker, model=User)
    application.include_router(router)

    with start_server(application, server_port) as server:
        print(get(f'http://{server.host}:{server.port}/'))
