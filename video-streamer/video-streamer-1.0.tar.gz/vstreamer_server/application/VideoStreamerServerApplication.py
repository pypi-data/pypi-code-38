from PySide2 import QtCore

import vstreamer_utils


class VideoStreamerServerApplication(QtCore.QCoreApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("video_streamer_server")
        self.logger = vstreamer_utils.make_logger()
        vstreamer_utils.set_signal_handlers(self)

        self.logger.info("Started server application")
