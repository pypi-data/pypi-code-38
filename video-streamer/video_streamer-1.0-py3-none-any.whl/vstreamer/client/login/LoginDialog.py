from PySide2 import QtWidgets

import vstreamer_utils


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("LoginDialog.ui", self)
        self.remote_host = None
        self.button.clicked.connect(self._on_click_ok)

    def _on_click_ok(self):
        self.remote_host = self.host_edit.text()
        self.accept()
