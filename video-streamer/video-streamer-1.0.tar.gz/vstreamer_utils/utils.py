import inspect
import logging
import pathlib
import signal
import time

import pkg_resources
from PySide2 import QtCore, QtUiTools

# not imported
from vstreamer.client.list import DirectoryInfoView, PropertiesWidget
from vstreamer.client.player import VideoPlayer, VideoPlayerBar


class _SelfUILoader(QtUiTools.QUiLoader):
    def __init__(self, widget):
        QtUiTools.QUiLoader.__init__(self, widget)
        self.widget = widget
        self.custom_widgets = dict()
        self.custom_widgets[DirectoryInfoView.__name__] = DirectoryInfoView
        self.custom_widgets[PropertiesWidget.__name__] = PropertiesWidget
        self.custom_widgets[VideoPlayer.__name__] = VideoPlayer
        self.custom_widgets[VideoPlayerBar.__name__] = VideoPlayerBar

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.widget:
            return self.widget
        else:
            if class_name in self.availableWidgets():
                widget = QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            else:
                try:
                    widget = self.custom_widgets[class_name](parent=parent)
                except (TypeError, KeyError) as e:
                    raise Exception(
                        'No custom widget ' + class_name + ' found in customWidgets param of UiLoader __init__.')
            if self.widget:
                setattr(self.widget, name, widget)
            return widget

SERVER_PORT = 5655
SERVER_VIDEO_PORT = 5656
DBUS_NAME = "com.video_streamer.ServerController"

def is_video_file(file):
    file = pathlib.Path(file)
    return file.is_file() and file.suffix in (".mkv", ".mp4")


def load_ui(file, widget):
    frame = inspect.stack()[1]  # get stack frame of the caller
    module_name = inspect.getmodule(frame[0]).__name__  # caller module name
    ui_file_path = pkg_resources.resource_filename(module_name, file)
    _SelfUILoader(widget).load(str(ui_file_path))


def size_to_string(size, suffix="B"):
    if size < 10240:
        return "%d %s" % (size, suffix)
    size >>= 10
    if size < 10240:
        return "%d Ki%s" % (size, suffix)
    size >>= 10
    if size < 10240:
        return "%d Mi%s" % (size, suffix)
    size >>= 10
    return "%d Gi%s" % (size, suffix)


def format_time(time_ms):
    time_s = time_ms / 1000
    if time_s >= 3600:
        return time.strftime("%H:%M:%S", time.localtime(time_s))
    else:
        return time.strftime("%M:%S", time.localtime(time_s))


def make_logger():
    logging.basicConfig(datefmt="%Y.%m.%d %H:%M:%S",
                        format="[%(asctime)s] %(name)s[%(levelname)s]: %(message)s")
    app_name = QtCore.QCoreApplication.applicationName()
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    logger = logging.getLogger(QtCore.QCoreApplication.applicationName())
    return logger


def set_signal_handlers(app):
    def handle(signum, frame):
        QtCore.QCoreApplication.quit()

    signal_timer = QtCore.QTimer(app)
    signal_timer.start(50)
    signal_timer.timeout.connect(lambda: None)

    signal.signal(signal.SIGINT, handle)
    signal.signal(signal.SIGTERM, handle)


def log_info(message):
    QtCore.QCoreApplication.instance().logger.info(message)
