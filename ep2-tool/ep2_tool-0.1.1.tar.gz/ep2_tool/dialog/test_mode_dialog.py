from PyQt5.QtWidgets import QDialog
from ep2_tool.ui.test_mode import Ui_Dialog


class TestModeDialog(QDialog, Ui_Dialog):

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)