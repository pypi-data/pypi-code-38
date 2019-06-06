from PySide2 import QtWidgets, QtGui, QtCore

import vstreamer_utils


class VideoPlayerBar(QtWidgets.QWidget):
    playing_state_changed = QtCore.Signal(bool)
    muted_changed = QtCore.Signal(bool)
    position_changed = QtCore.Signal(int)
    volume_changed = QtCore.Signal(int)
    fullscreen_requested = QtCore.Signal()
    stop_requested = QtCore.Signal()


    def __init__(self, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("VideoPlayerBar.ui", self)
        self._playing = None
        self._muted = None

        self.forward_toolbutton.setIcon(QtGui.QIcon(":/icons/FastForward.png"))
        self.rewind_toolbutton.setIcon(QtGui.QIcon(":/icons/FastRewind.png"))
        self.fullscreen_toolbutton.setIcon(QtGui.QIcon(":/icons/Fullscreen.png"))
        self.stop_toolbutton.setIcon(QtGui.QIcon(":/icons/Stop.png"))
        self.update_current_video_time(0, 0)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.set_muted(False)
        self.set_playing(False)

        self.play_pause_toolbutton.clicked.connect(lambda: self.set_playing(not self._playing))
        self.slider.sliderMoved.connect(self._handle_slider_drag_value)
        self.rewind_toolbutton.clicked.connect(self._handle_rewind)
        self.forward_toolbutton.clicked.connect(self._handle_forward)
        self.stop_toolbutton.clicked.connect(self.stop_requested)
        self.fullscreen_toolbutton.clicked.connect(self.fullscreen_requested)
        self.volume_toolbutton.clicked.connect(self._handle_mute_click)
        self.volume_slider.sliderMoved.connect(self.volume_changed)

    def _handle_mute_click(self):
        self.set_muted(not self._muted)

    def _handle_rewind(self):
        cur_val = self.slider.value()
        max_val = self.slider.maximum()
        next_val = cur_val - 5000
        if next_val < 0:
            next_val = 0
        self.update_current_video_time(next_val, max_val)
        self._handle_slider_drag_value(next_val)

    def _handle_forward(self):
        cur_val = self.slider.value()
        max_val = self.slider.maximum()
        next_val = cur_val + 5000
        if next_val > max_val:
            next_val = max_val
        self.update_current_video_time(next_val, max_val)
        self._handle_slider_drag_value(next_val)

    def _handle_slider_drag_value(self, value):
        self.update_current_video_time(value, self.slider.maximum())
        self.position_changed.emit(value)

    def update_current_video_time(self, current_time_ms, total_time_ms):
        self.length_label.setText(
            vstreamer_utils.utils.format_time(
                current_time_ms) + "/" + vstreamer_utils.utils.format_time(total_time_ms))
        self.slider.setRange(0, total_time_ms)
        if not self.slider.isSliderDown():
            self.slider.setValue(current_time_ms)

    def set_muted(self, muted):
        if self._muted == muted:
            return
        self._muted = muted
        if muted:
            self.volume_toolbutton.setIcon(QtGui.QIcon(":/icons/VolumeOff.png"))
        else:
            self.volume_toolbutton.setIcon(QtGui.QIcon(":/icons/VolumeDown.png"))
        self.muted_changed.emit(self._muted)

    def set_playing(self, playing):
        if playing == self._playing:
            return
        if playing:
            self.play_pause_toolbutton.setIcon(QtGui.QIcon(":/icons/Pause.png"))
            self._playing = playing
        else:
            self.play_pause_toolbutton.setIcon(QtGui.QIcon(":/icons/Play.png"))
            self._playing = playing
        self.playing_state_changed.emit(self._playing)

    def set_volume(self, volume):
        self.volume_slider.setValue(volume)
        if volume == 0:
            self.volume_toolbutton.setIcon(QtGui.QIcon(":/icons/VolumeOff.png"))
        else:
            self.volume_toolbutton.setIcon(QtGui.QIcon(":/icons/VolumeDown.png"))
        self.volume_changed.emit(volume)
