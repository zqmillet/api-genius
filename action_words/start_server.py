from typing import Union
from time import sleep
from contextlib import contextmanager
from multiprocessing import Process

from pydantic import BaseModel
from pydantic import Field
from uvicorn import run
from fastapi import FastAPI

from .is_open_port import is_open_port

class Server(BaseModel):
    """
    this is the return value of function start_server,
    which contains informations of start.
    """
    host: str = Field(default='localhost')
    port: int

@contextmanager
def start_server(
        application: FastAPI,
        port: int,
        interval: Union[int, float] = 0.5,
        log_level: str = 'critical'
    ) -> Server:
    """
    this context manager is used to start an application
    in a independent process.
    """
    assert not is_open_port(port)

    process = Process(
        target=run,
        args=(application,),
        kwargs={'port': port,'log_level': log_level},
        daemon=True
        )
    process.start()

    while not is_open_port(port):
        sleep(interval)

    yield Server(port=port)

    process.terminate()
