from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *


class DotViewer(QWidget):
    def __init__(self, image_viewer):
        super().__init__()
        self.setWindowTitle("Dot viewer")

        self._image_viewer = image_viewer
        self.tool_bar = QToolBar()
        self.edit = QTextEdit()
        _layout = QVBoxLayout()
        _layout.addWidget(self.tool_bar)
        _layout.addWidget(self.edit)
        _layout.setContentsMargins(0, 0, 0, 0)
        self.set_dot('')

        self.setLayout(_layout)
        self._setup_toolbar()  # TODO: do something with that toolbar

    def _setup_toolbar(self):
        "Populate the toolbar"
        self.tool_bar.addAction('render', lambda: self.set_dot(self.get_dot()))

    def set_dot(self, source, compile_and_send=True):
        self.edit.setText(source)
        if compile_and_send:
            self._image_viewer.set_dot(source)

    def get_dot(self):
        return self.edit.toPlainText()
