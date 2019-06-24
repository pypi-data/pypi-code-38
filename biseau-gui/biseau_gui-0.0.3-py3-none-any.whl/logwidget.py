from PySide2.QtWidgets import *
from PySide2.QtCore import *


class LogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget()
        self.log_edit = QPlainTextEdit()

        _layout = QVBoxLayout()
        _layout.addWidget(self.tab_widget)
        _layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(_layout)

        self.tab_widget.setTabPosition(QTabWidget.South)
        self.add_widget(self.log_edit, "ASP syntax error")

    def add_widget(self, widget, name):
        self.tab_widget.addTab(widget, name)

    def add_message(self, msg):
        self.log_edit.appendPlainText(msg)
