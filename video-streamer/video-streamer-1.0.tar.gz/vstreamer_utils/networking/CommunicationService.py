import pickle
import struct

from PySide2 import QtCore, QtNetwork

import vstreamer_utils
from vstreamer_utils import networking


class MessageHeader:
    HEADER = bytearray("VSTR", encoding="ascii")
    SIZE = 12

    def __init__(self, size):
        self.size = size

    def to_data(self):
        return MessageHeader.HEADER + struct.pack("!Q", self.size)

    @staticmethod
    def from_data(byte_array):
        if len(byte_array) != 12:
            raise ValueError("Message header length is invalid")
        if byte_array[:4] != MessageHeader.HEADER:
            raise ValueError("Message header is invalid")
        return MessageHeader(int(struct.unpack("!Q", byte_array[4:])[0]))


class CommunicationService(QtCore.QObject):
    received_request = QtCore.Signal(networking.Request)
    received_response = QtCore.Signal(networking.Response)
    disconnected = QtCore.Signal(QtNetwork.QTcpSocket)
    error_occurred = QtCore.Signal(vstreamer_utils.Error)

    def __init__(self, socket, parent=None):
        super().__init__(parent)
        if socket.state() != QtNetwork.QAbstractSocket.SocketState.ConnectedState:
            raise ValueError("Socket is not connected")

        self.socket = socket
        self.socket.setParent(self)
        self._data = bytearray()
        self._size_left = 0
        self._connect_signals()
        vstreamer_utils.log_info("Host %s:%d - created CommunicationService" %
                                 (self.socket.peerAddress().toString(), self.socket.peerPort()))

    def write_message(self, message):
        if not isinstance(message, networking.Request) and not isinstance(message, networking.Response):
            raise TypeError("Message is not a Request or a Response")
        data = pickle.dumps(message, pickle.DEFAULT_PROTOCOL, fix_imports=False)
        data_length = len(data)
        data = MessageHeader(data_length).to_data() + data
        self.socket.write(data)

    def _connect_signals(self):
        self.socket.disconnected.connect(self._handle_disconnected)
        self.socket.error.connect(self._handle_error)
        self.socket.readyRead.connect(self._handle_data_ready)

    def _handle_disconnected(self):
        self.socket.disconnected.disconnect(self._handle_disconnected)
        self.socket.error.disconnect(self._handle_error)
        self.socket.readyRead.disconnect(self._handle_data_ready)
        self.disconnected.emit(self.socket)

    def _handle_error(self):
        self.socket.disconnected.disconnect(self._handle_disconnected)
        self.socket.error.disconnect(self._handle_error)
        self.socket.readyRead.disconnect(self._handle_data_ready)
        self.error_occurred.emit(vstreamer_utils.Error(self.socket.errorString(), vstreamer_utils.ErrorLevel.ERROR))

    def _read_data(self, size):
        data = self.socket.read(size).data()
        if len(data) != size:
            raise RuntimeError("Could not read message data")
        return data

    def _unpack_data(self):
        message = None
        try:
            message = pickle.loads(self._data, fix_imports=False)
        except pickle.UnpicklingError:
            raise RuntimeError("Received message is unreadable")
        return message

    def _emit_message(self, message):
        if isinstance(message, networking.Request):
            self.received_request.emit(message)
        elif isinstance(message, networking.Response):
            self.received_response.emit(message)
        else:
            raise TypeError("Received message is not a Request or a Response")

    def _handle_data_ready(self):
        try:
            available = self.socket.bytesAvailable()
            if self._size_left == 0:
                if available >= MessageHeader.SIZE:
                    data = self._read_data(MessageHeader.SIZE)
                    header = MessageHeader.from_data(data)
                    self._size_left = header.size
                else:
                    return

            size_to_read = min(self._size_left, available)
            data = self._read_data(size_to_read)
            available -= size_to_read
            self._size_left -= size_to_read
            self._data += data

            if self._size_left == 0:
                message = self._unpack_data()
                self._data = bytearray()
                self._emit_message(message)

            if available != 0:
                self._handle_data_ready()

        except (RuntimeError, TypeError, ValueError) as exc:
            self.socket.setErrorString(str(exc))
            self._handle_error()
