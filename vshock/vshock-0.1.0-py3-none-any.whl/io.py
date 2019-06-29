import struct
import atexit
import os
import io
from os.path import abspath


def create_fifo(path):
    """
    Make an fifo(named pipe) at specific path.
    And remove it at exit.
    """
    os.mkfifo(path)
    print("A fifo is created at %s." % abspath(path))
    atexit.register(os.unlink, path)


class JoystickStream:
    def __init__(self, path):
        self.path = path
        self.file = None

    def ensure_opened_file(self):
        if not self.file or self.file.closed:
            self.file = io.open(self.path, 'wb').__enter__()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.file:
            self.file.__exit__()

    def emit(self, message):
        self.ensure_opened_file()
        input_type = message['input_type']
        if input_type == 1:
            data = struct.pack('8b', 0, 0, 0, 0, message['value'], 0, 1,
                               message['button_number'])
            self.file.write(data)
            self.file.flush()
        elif input_type == 2:
            data = struct.pack('8b', 0, 0, 0, 0, 0, message['value'], 2,
                               message['button_number'])
            self.file.write(data)
            self.file.flush()
