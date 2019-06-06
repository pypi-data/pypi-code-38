import ctypes.util
import platform
import urllib.parse
import vlc
from PySide2 import QtCore, QtWidgets, QtGui, QtMultimediaWidgets

import vstreamer_utils
from vstreamer.client.player import VideoPlayerBar

# set up vsnprintf
if platform.system() == "Windows":
    vsnprintf = ctypes.cdll.msvcrt.vspnrintf
else:
    libc = ctypes.cdll.LoadLibrary(ctypes.util.find_library('c'))
    vsnprintf = libc.vsnprintf
vsnprintf.restype = ctypes.c_int
vsnprintf.argtypes = (
    ctypes.c_char_p,
    ctypes.c_size_t,
    ctypes.c_char_p,
    ctypes.c_void_p)


class VideoPlayer(QtWidgets.QWidget):
    error_occurred = QtCore.Signal(vstreamer_utils.Error)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.remote_host = None
        self.port = None

        self.player_widget = QtMultimediaWidgets.QVideoWidget(self)
        self.player_widget.setMouseTracking(True)
        self.player_widget.setGeometry(0, 0, self.width(), self.height())
        self.bar = VideoPlayerBar(self)
        self.bar.setMouseTracking(True)
        self.bar.setGeometry(0, max(0, self.height() - 51), self.width(), 51)
        self.bar.setVisible(False)
        self.bar.destroyed.connect(lambda: print("Destroyed bar"))

        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtCore.Qt.black)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        self.setMouseTracking(True)

        @vlc.CallbackDecorators.LogCb
        def log_callback(data, level, ctx, fmt, args):
            self._log_callback(level, fmt, args)
        self._save_log_callback = log_callback

        def player_event_handler(event_type):
            QtCore.QMetaObject.invokeMethod(self, "_player_event_handler", QtCore.Qt.QueuedConnection,
                                            QtCore.QGenericArgument("int", event_type.type))
        self._save_player_event_handler = player_event_handler

        self._instance = vlc.Instance()
        self._instance.log_set(log_callback, None)
        self._player = self._instance.media_player_new()
        self._events = self._player.event_manager()
        self._events.event_attach(vlc.EventType.MediaPlayerEndReached, player_event_handler)
        self._events.event_attach(vlc.EventType.MediaPlayerTimeChanged, player_event_handler)
        self._events.event_attach(vlc.EventType.MediaPlayerPositionChanged, player_event_handler)
        self._events.event_attach(vlc.EventType.MediaPlayerLengthChanged, player_event_handler)

        if platform.system() == "Linux":  # for Linux using the X Server
            self._player.set_xwindow(int(self.player_widget.winId()))
        elif platform.system() == "Windows":  # for Windows
            self._player.set_hwnd(int(self.player_widget.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self._player.set_nsobject(int(self.player_widget.winId()))
        else:
            raise RuntimeError("Multimedia is not supported on this platform")

        self.bar.playing_state_changed.connect(self._player_set_playing)
        self.bar.position_changed.connect(self._player_set_position)
        self.bar.volume_changed.connect(self._player_set_volume)
        self.bar.muted_changed.connect(self._player_set_muted)
        self.bar.fullscreen_requested.connect(self._toggle_fullscreen)
        self.bar.stop_requested.connect(self._player_stop)

    def resizeEvent(self, event):
        self.player_widget.setGeometry(0, 0, event.size().width(), event.size().height())
        self.bar.setGeometry(0, max(0, event.size().height() - 51), event.size().width(), 51)

    def mouseMoveEvent(self, event):
        if self.height() - event.y() <= 51:
            self.bar.setVisible(True)
        else:
            self.bar.setVisible(False)

    def mouseDoubleClickEvent(self, event):
        self._toggle_fullscreen()

    def set_remote_host(self, remote_host, port):
        self.remote_host = remote_host
        self.port = port
        vstreamer_utils.log_info("Initialized VideoPlayer with %s:%d" % (remote_host, port))

    def play_video(self, video_file_entry):
        encoded = urllib.parse.quote(video_file_entry.path)
        url = "rtsp://%s:%d%s" % (self.remote_host, self.port, encoded)
        media = self._instance.media_new(url)
        media.parse()
        self._player.set_media(media)
        self._player.play()
        self.bar.set_playing(True)
        vstreamer_utils.log_info("Playing video from '%s'" % url)

    def _toggle_fullscreen(self):
        if self.parent() is not None:
            self._parent.removeTab(0)
            self.setParent(None)
            self._parent.window().hide()
            self.showFullScreen()
        else:
            self._parent.window().show()
            self.hide()
            self._parent.insertTab(0, self, "Player")
            self._parent.setCurrentIndex(0)
            self.show()

    @QtCore.Slot(int)
    def _player_event_handler(self, event_type):
        curr_time = self._player.get_time()
        full_length = self._player.get_length()
        if event_type in (vlc.EventType.MediaPlayerTimeChanged, vlc.EventType.MediaPlayerPositionChanged,
                          vlc.EventType.MediaPlayerLengthChanged):
            self.bar.update_current_video_time(curr_time, full_length)
        elif event_type == vlc.EventType.MediaPlayerEndReached:
            self.bar.update_current_video_time(0, full_length)
            self.bar.set_playing(False)

    def _player_set_volume(self, volume):
        self._player.audio_set_volume(volume)

    def _player_set_position(self, value):
        if self._player.get_media() is None:
            return
        self._player.set_time(value)

    def _player_set_playing(self, playing):
        if self._player.get_media() is None:
            self.bar.set_playing(False)
            return
        if playing:
            self._player.set_pause(0)
        else:
            self._player.set_pause(1)

    def _player_set_muted(self, muted):
        self._player.audio_set_mute(muted)

    def _player_stop(self):
        self._player.stop()
        self._player.set_media(None)
        self.bar.set_playing(False)
        self.bar.update_current_video_time(0, 0)
        self.hide()
        self.show()

    @staticmethod
    def _make_msg(fmt, args):
        buf_length = 2048
        msg = ctypes.create_string_buffer(buf_length)
        vsnprintf(msg, buf_length, fmt, args)
        return msg.value.decode("utf-8")

    def _log_callback(self, level, fmt, args):
        msg = VideoPlayer._make_msg(fmt, args)
        if level in (vlc.LogLevel.WARNING, vlc.LogLevel.ERROR):
            self.error_occurred.emit(vstreamer_utils.Error(msg, vstreamer_utils.ErrorLevel.WARNING))
        elif level == vlc.LogLevel.NOTICE:
            vstreamer_utils.log_info(msg)
