import pathlib

from PySide2 import QtCore

import vstreamer_utils
from vstreamer_utils import networking


class RequestHandler(QtCore.QObject):
    error_occurred = QtCore.Signal(vstreamer_utils.Error)

    def __init__(self, communication_service, directory_tree, parent=None):
        super().__init__(parent)
        self.communication_service = communication_service
        self.directory_tree = directory_tree
        self.communication_service.received_request.connect(self._handle_request)
        self.communication_service.received_response.connect(self._handle_response)
        vstreamer_utils.log_info("host %s - created RequestHandler" %
                                 self.communication_service.socket.peerAddress().toString())

    def _emit_error(self, message):
        formatted_msg = "Host %s -  %s" % (
        self.communication_service.socket.peerAddress().toString(), message)
        self.error_occurred.emit(vstreamer_utils.Error(formatted_msg, vstreamer_utils.ErrorLevel.WARNING))

    def _handle_request(self, request):
        if not isinstance(request, networking.Request):
            self.communication_service.write_message(networking.ErrorResponse("Received message that is not a request"))
            self._emit_error("Received message that is not a request")
        if isinstance(request, networking.DirectoryInfoRequest):
            self._handle_directory_info_request(request)
        elif isinstance(request, networking.AdditionalEntryPropertiesRequest):
            self._handle_additional_entry_properties_request(request)
        else:
            self.communication_service.write_message(networking.ErrorResponse("Received invalid request"))
            self._emit_error("Received invalid request")

    def _handle_response(self):
        self.communication_service.write_message(networking.ErrorResponse("Received message that is not a request"))
        self._emit_error("Received message that is not a request")

    def _handle_directory_info_request(self, request):
        vstreamer_utils.log_info("Host %s - received directory info request for '%s'" %
                                 (self.communication_service.socket.peerAddress().toString(),
                                  request.path))
        if request.path not in self.directory_tree.directories:
            msg = "Directory '%s' does not exist" % request.path
            self.communication_service.write_message(networking.ErrorResponse(msg))
            self._emit_error(msg)
            return
        entries = self.directory_tree.directories[request.path].light_copy()
        self.communication_service.write_message(networking.DirectoryInfoResponse(entries))

    def _handle_additional_entry_properties_request(self, request):
        vstreamer_utils.log_info("Host %s - received additional entry properties request for '%s'"
                                 % (self.communication_service.socket.peerAddress().toString(),
                                    request.filepath))
        path_object = pathlib.Path(request.filepath)
        dir_path = str(path_object.parent)
        filename = str(path_object.name)

        if dir_path not in self.directory_tree.directories:
            msg = "Directory '%s' does not exist" % request.path
            self.communication_service.write_message(networking.ErrorResponse(msg))
            self._emit_error(msg)
            return

        directory_entry = self.directory_tree.directories[dir_path]
        for entry in directory_entry.entries:
            if filename == entry.filename:
                self.communication_service.write_message(
                    networking.AdditionalEntryPropertiesResponse(request.filepath, entry.additional_properties()))
                return

        msg = "File '%s' does not exist" % request.filepath
        self.communication_service.write_message(networking.ErrorResponse(msg))
        self._emit_error(msg)
