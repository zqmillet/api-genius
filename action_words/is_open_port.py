from socket import socket
from socket import AF_INET
from socket import SOCK_STREAM

def is_open_port(port: int) -> bool:
    with socket(AF_INET, SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0
