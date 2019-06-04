import socket
from urllib.parse import urlparse

from matrix_client.client import MatrixClient
from matrix_client.errors import MatrixRequestError
from matrix_client.room import Room

from serverchecks.alerts import AbstractAlert


class MatrixAlert(AbstractAlert):
    """
    Matrix alert class using matrix_client library (aka Matrix Python SDK)
    https://github.com/matrix-org/matrix-python-sdk
    https://matrix.org/docs/spec/client_server/r0.4.0.html
    """
    name = "Matrix"

    def __init__(self, **kwargs) -> None:
        self.username: str = kwargs.get('username')
        self.password: str = kwargs.get('password')
        self.server: str = kwargs.get('server')
        self.room_name: str = kwargs.get('room')
        self.recipients = kwargs.get('recipients')

        self.domain: str = urlparse(self.server).hostname
        self.client: MatrixClient = MatrixClient(self.server)

    async def open(self) -> None:
        self.token: str = self.client.login(username=self.username, password=self.password, device_id=socket.getfqdn())

        try:
            self.room: Room = self.client.join_room(f'#{self.room_name}:{self.domain}')
        except MatrixRequestError as e:
            if e.code == 404:
                self.room = self.client.create_room(self.room_name, False, self.recipients)
            else:
                raise e

    async def alert(self, message: str) -> None:
        self.room.send_text(message)

    async def close(self) -> None:
        self.client.logout()

    def __str__(self) -> str:
        return f'<{self.name}: ID={self.username} room={self.room_name}>'


alert_class = MatrixAlert
