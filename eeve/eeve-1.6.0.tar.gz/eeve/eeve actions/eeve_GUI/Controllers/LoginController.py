from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QWidget, QMessageBox  # pylint: disable=no-name-in-module
from .EventsController import EventsController
from .. import GuiController

from eeve import database


class LoginController(GuiController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @pyqtSlot(str, str)
    def login(self, user_name: str, password: str) -> bool:
        if database.check_credentials(user_name, password) or True:
            self.load_controller(EventsController)
        else:
            QMessageBox.warning(None, 'Aviso', 'Os dados inseridos estão incorretos.')



