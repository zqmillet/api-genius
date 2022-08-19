from contextlib import contextmanager
from multiprocessing import Process
from uvicorn import run
from time import sleep

from .is_open_port import is_open_port

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

@contextmanager
def start_server(application, port) -> Server:
    assert not is_open_port(port)

    process = Process(target=run, args=(application,), kwargs={'port': port, 'log_level': 'critical'}, daemon=True)
    process.start()

    while not is_open_port(port):
        sleep(0.5)

    yield Server('localhost', port)

    process.terminate()
