from PySide2 import QtCore, QtWidgets, QtGui

import vstreamer_utils


class FileEntryWidget(QtWidgets.QWidget):
    FIXED_SIZE = QtCore.QSize(120, 140)

    def __init__(self, file_entry=None, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("FileEntryWidget.ui", self)
        self._file_entry = None
        if file_entry is not None:
            self.set_file_entry(file_entry)

    def set_file_entry(self, file_entry):
        self._file_entry = file_entry
        if self._file_entry is not None:
            if self._file_entry.image is not None:
                image = QtGui.QImage.fromData(QtCore.QByteArray(self._file_entry.image))
                self.image_label.setPixmap(QtGui.QPixmap.fromImage(image))
            elif self._file_entry.is_video():
                self.image_label.setPixmap(QtGui.QPixmap(":/icons/VideoFileIcon.png"))
            else:
                self.image_label.setPixmap(QtGui.QPixmap(":/icons/DirectoryIcon.png"))
            self.title_label.setText(self._file_entry.properties["Filename"])

    def get_file_entry(self):
        return self._file_entry
