from PySide2 import QtCore
from PySide2.QtCore import QObject

import vstreamer_utils
from vstreamer.directories import DirectoryCache
from vstreamer_utils.model import DirectoryInfo, AdditionalEntryProperties
from vstreamer_utils.networking import DirectoryInfoRequest, AdditionalEntryPropertiesRequest, \
    DirectoryInfoResponse, AdditionalEntryPropertiesResponse, ErrorResponse


class DirectoryService(QObject):
    directories_ready = QtCore.Signal(DirectoryInfo)
    additional_properties_ready = QtCore.Signal(str, AdditionalEntryProperties)
    error_occurred = QtCore.Signal(vstreamer_utils.Error)

    def __init__(self, communication_service, parent=None):
        super().__init__(parent)
        self.communication_service = communication_service
        self.communication_service.received_response.connect(self._handle_response)
        self._cache = DirectoryCache()
        vstreamer_utils.log_info("Host %s:%d - created DirectoryService" %
                                 (self.communication_service.socket.peerAddress().toString(),
                                  self.communication_service.socket.peerPort()))

    def get_directory_info(self, path="/"):
        vstreamer_utils.log_info("Querying DirectoryInfo for '%s'" % path)
        cached_directory = self._cache.get_directory(path)
        if cached_directory is not None:
            self.directories_ready.emit(cached_directory)
        else:
            self.communication_service.write_message(DirectoryInfoRequest(path))

    def get_additional_info(self, filepath):
        vstreamer_utils.log_info("Querying AdditionalEntryProperties for '%s'" % filepath)
        cached_properties = self._cache.get_additional_properties(filepath)
        if cached_properties is not None:
            self.additional_properties_ready.emit(filepath, cached_properties)
        else:
            self.communication_service.write_message(AdditionalEntryPropertiesRequest(filepath))

    def _handle_response(self, response):
        # TODO logs
        if isinstance(response, DirectoryInfoResponse):
            self._cache.store_directory(response.directory_info)
            self.directories_ready.emit(response.directory_info)
        elif isinstance(response, AdditionalEntryPropertiesResponse):
            self._cache.store_additional_properties(response.filepath, response.additional_properties)
            self.additional_properties_ready.emit(response.filepath, response.additional_properties)
        elif isinstance(response, ErrorResponse):
            self.error_occurred.emit(vstreamer_utils.Error(response.error_string, vstreamer_utils.ErrorLevel.ERROR))
        else:
            self.error_occurred.emit(vstreamer_utils.Error("Unknown response received", vstreamer_utils.ErrorLevel.ERROR))

