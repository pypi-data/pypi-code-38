import pkg_resources
from PySide2 import QtCore, QtWidgets, QtGui

import vstreamer_utils


class VideoStreamerApplication(QtWidgets.QApplication):
    def __init__(self, args):
        # Qt WebEngine init fix
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

        super().__init__(args)

        # resources
        rcc_path = str(pkg_resources.resource_filename("vstreamer", "resources/resources.rcc"))
        QtCore.QResource.registerResource(rcc_path)

        # application properties
        self.setApplicationName("video_streamer")
        self.setWindowIcon(QtGui.QIcon(":/icons/Avatar.png"))

        self.logger = vstreamer_utils.make_logger()
        vstreamer_utils.set_signal_handlers(self)

        self.logger.info("Started client application")
