from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM

def is_open_port(port: int) -> bool:
    """
    this function is used to check whether a port is open.
    """
    with socket(AF_INET, SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0
