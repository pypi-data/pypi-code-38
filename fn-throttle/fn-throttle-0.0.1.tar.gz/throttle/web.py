import json
import logging
import socket
from threading import Thread

from .configs import PORT_CHOICES


class MasterServer(Thread):
    """
    | Command                        | Respond      |
    | throttle::ping                 | {port}       |
    | throttle::regist::key::params  | ok/fail      |
    | throttle::admit::key           | admit/forbid |
    """
    def __init__(self, controller_clz, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller_clz = controller_clz
        self.socket = socket.socket()
        for port in PORT_CHOICES:
            # noinspection PyBroadException
            try:
                self.socket.bind(('', port))
            except:  # noqa
                pass
            else:
                self.port = port
                self.socket.listen(5)
                logging.info(f'Throttle master server run on port: {self.port}')
                break
        else:
            raise Exception('No available port')

    def run(self) -> None:
        controller = self.controller_clz()
        while True:
            client, _ = self.socket.accept()
            try:
                command = client.recv(2048).decode('utf8')
                cmds = command.split('::')
                if cmds[0] == 'throttle':
                    if cmds[1] == 'ping':
                        client.send(str(self.port).encode('utf8'))
                    elif cmds[1] == 'regist':
                        key = cmds[2]
                        params = json.loads(cmds[3])
                        if controller.registry(key, params):
                            client.send(b'ok')
                        else:
                            client.send(b'fail')
                    elif cmds[1] == 'admit':
                        key = cmds[2]
                        if controller.admit(key):
                            client.send(b'admit')
                        else:
                            client.send(b'forbid')
            except Exception as e:
                logging.error(e, exc_info=True)
            finally:
                # noinspection PyBroadException
                try:
                    client.close()
                except:  # noqa
                    pass


class SlaveClient:

    def __init__(self, port):
        self.port = port

    def ping(self, port=None) -> bool:
        """ Try to ping master node """
        self.port = port or self.port
        s = socket.socket()
        s.settimeout(0.1)
        # noinspection PyBroadException
        try:
            s.connect(('127.0.0.1', self.port))
            s.send(b'throttle::ping')
            s.recv(1024).decode('utf8')
            s.close()
        except:  # noqa
            logging.debug(f'Slave client fail to connect local port: {self.port}')
            return False
        else:
            logging.info(f'Slave client succeed to connect local port: {self.port}')
            return True

    def regist(self, key: str, params: dict) -> bool:
        s = socket.socket()
        s.settimeout(3)
        s.connect(('127.0.0.1', self.port))
        s.send(f'throttle::regist::{key}::{json.dumps(params)}'.encode('utf8'))
        respond = s.recv(1024).decode('utf8')
        s.close()
        return respond == 'ok'

    def admit(self, key: str) -> bool:
        s = socket.socket()
        s.settimeout(3)
        s.connect(('127.0.0.1', self.port))
        s.send(f'throttle::admit::{key}'.encode('utf8'))
        respond = s.recv(1024).decode('utf8')
        s.close()
        return respond == 'admit'
