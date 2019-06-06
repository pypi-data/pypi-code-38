from PySide2 import QtCore, QtNetwork

import vstreamer_utils
from vstreamer_server import communication
from vstreamer_utils import networking


class CommunicationServer(QtCore.QObject):
    error_occurred = QtCore.Signal(vstreamer_utils.Error)

    def __init__(self, port, directory_tree, parent=None):
        super().__init__(parent)
        self.port = int(port)
        self.directory_tree = directory_tree
        self.server = QtNetwork.QTcpServer(self)

        self.server.newConnection.connect(self._handle_new_connection)
        self.server.acceptError.connect(self._handle_accept_error)
        vstreamer_utils.log_info("Initialized communication server")

    def start(self):
        if not self.server.listen(port=self.port):
            raise RuntimeError("Could not start listening for connections on port: %d" % self.port)
        vstreamer_utils.log_info("Started listening for tcp connections on port %d" % self.port)

    def _handle_accept_error(self):
        self.error_occurred.emit(vstreamer_utils.Error(self.server.errorString(), vstreamer_utils.ErrorLevel.ERROR))

    def _handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        vstreamer_utils.log_info(
            "Host %s:%d connected" % (socket.peerAddress().toString(), socket.peerPort()))

        communication_service = networking.CommunicationService(socket, self)
        request_handler = communication.RequestHandler(communication_service, self.directory_tree, communication_service)

        request_handler.error_occurred.connect(self._handle_error)
        communication_service.error_occurred.connect(self._handle_error)
        communication_service.disconnected.connect(self._handle_disconnected)

    def _handle_error(self, error):
        sender = self.sender()
        if error.level in (vstreamer_utils.ErrorLevel.ERROR, vstreamer_utils.ErrorLevel.CRITICAL):
            sender.deleteLater()
        self.error_occurred.emit(error)

    def _handle_disconnected(self, socket):
        sender = self.sender()
        vstreamer_utils.log_info(
            "Host %s:%d disconnected" % (socket.peerAddress().toString(), socket.peerPort()))
        sender.deleteLater()
