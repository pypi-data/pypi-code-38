from shioaji.backend.http import HttpApi as _http
from shioaji.backend.socket import Wrapper as _socket


def get_backends():
    apis = {
        'http': _http,
        'socket': _socket,
    }
    return apis
