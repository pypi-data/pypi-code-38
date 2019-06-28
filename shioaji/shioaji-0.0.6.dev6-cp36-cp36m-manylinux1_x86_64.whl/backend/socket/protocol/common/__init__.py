from shioaji.backend.socket.protocol.common.handler import (
    ping_alive,
    login_in,
    login_out,
    logout_in,
)

tr_map = {
    20000: (login_in, login_out),
    20001: (logout_in, None),
}

__all__ = [
    'tr_map',
    'ping_alive',
    'login_in',
    'login_out',
    'logout_in',
]
