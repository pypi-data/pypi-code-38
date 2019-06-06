from PySide2 import QtCore, QtWidgets

import vstreamer_utils
from vstreamer import directories
from vstreamer.client import login
from vstreamer.client.login import LoginDialog
from vstreamer_utils.networking import CommunicationService


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("MainWindow.ui", self)
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self._on_application_quit)
        self.error_handler = vstreamer_utils.ErrorHandler(
            vstreamer_utils.ErrorHandlerType.GUI_HANDLER,
            self)
        self.remote_host = None
        self.socket = None
        self.response_handler = None
        self.communication_service = None
        self.directory_service = None
        vstreamer_utils.log_info("Initialized MainWindow")

    def connect_to_server(self):
        login_dialog = LoginDialog()
        if login_dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            self.remote_host = login_dialog.remote_host
            self.video_player.set_remote_host(self.remote_host, 5656)
            vstreamer_utils.log_info("Got remote host from input - '%s'" % self.remote_host)
        else:
            QtWidgets.QApplication.quit()
            return

        connect_dialog = login.ConnectDialog(self.remote_host)
        connect_dialog.connect_to_server()
        if connect_dialog.exec_() == QtWidgets.QDialog.DialogCode.Accepted:
            self.socket = connect_dialog.socket
            self._initialize_communication_socket()
        else:
            QtWidgets.QApplication.quit()
            return
        self.show()

    def _initialize_communication_socket(self):
        try:
            self.socket.setParent(self)
            vstreamer_utils.log_info("Host %s:%d - connected"
                                     % (
                                     self.socket.peerAddress().toString(), self.socket.peerPort()))
            self.communication_service = CommunicationService(self.socket, self)
            self.communication_service.error_occurred.connect(self.error_handler.handle_error)

            self.directory_service = directories.DirectoryService(self.communication_service, self)
            self.directory_service.directories_ready.connect(self._handle_directories_ready)
            self.directory_service.additional_properties_ready.connect(
                self._handle_additional_properties_ready)
            self.directory_service.error_occurred.connect(self.error_handler.handle_error)

            self.directory_info_view.play_requested.connect(self.video_player.play_video)
            self.directory_info_view.directory_requested.connect(
                lambda entry: self.directory_service.get_directory_info(entry.path))

            self.video_player.error_occurred.connect(self.error_handler.handle_error)

            self.directory_service.get_directory_info()
        except Exception as exc:
            self.error_handler.handle_exception(exc)

    def _handle_directories_ready(self, directory_info):
        self.directory_info_view.set_entries(directory_info)
        for file in directory_info.entries:
            if file.filename != "..":
                self.directory_service.get_additional_info(file.path)

    def _handle_additional_properties_ready(self, filename, additional_properties):
        self.directory_info_view.set_additional_properties(filename, additional_properties)

    def _on_application_quit(self):
        if self.communication_service is not None:
            host = self.socket.peerAddress().toString()
            port = self.socket.peerPort()
            self.communication_service.socket.disconnectFromHost()
            vstreamer_utils.log_info("Host %s:%d - disconnected" % (host, port))
        vstreamer_utils.log_info("Client is closing")
