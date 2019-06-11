# This Python file uses the following encoding: utf-8
import sys

from typing import Any, Tuple

from PyQt5.QtGui import QGuiApplication  # pylint: disable=no-name-in-module
from PyQt5.QtQml import QQmlApplicationEngine, QQmlComponent  # pylint: disable=no-name-in-module
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QMetaObject, Q_ARG, QVariant, QAbstractListModel, QModelIndex, Qt, QUrl  # pylint: disable=no-name-in-module
from PyQt5.QtWidgets import QListView, QComboBox, QWidget, QApplication, QMainWindow  # pylint: disable=no-name-in-module
from . import style

import os
base_path = os.path.dirname(__file__)

import eeve
from eeve.base_classes import Event, Trigger, Task, Action

primary_color = "#666666"


class Controller(QWidget):

    viewPushed = pyqtSignal(str, arguments=['viewName'])
    eventAdded = pyqtSignal()

    def __init__(self, engine: QQmlApplicationEngine):
        self.engine = engine
        self.active_controller_exit_point = lambda: None
        QWidget.__init__(self, flags=Qt.Widget)

    @pyqtSlot()
    def popView(self):
        self.active_controller_exit_point()


class GuiController(QWidget):
    def __init__(self, main_controller: Controller):
        self.main_controller = main_controller
        self.child = None  # this is here because when in use by the view it loses reference and is garbage collected
        QWidget.__init__(self, flags=Qt.Widget)

    def load_page(self):
        ...

    def unload_page(self):
        ...

    def regain_focus(self, unload_result):
        ...

    def _unload(self) -> Tuple[bool, Any]:
        if self.child:
            unloaded, unload_result = self.child._unload()
            if unloaded:
                self.child = None
                self.regain_focus(unload_result)
            return False, None
        else:
            return True, self.unload_page()

    def load_controller(self, controller: 'type(GuiController)', *args, view_posfix='', **kwargs):
        c = controller(main_controller=self.main_controller)
        self.child = c

        lower_first_char = lambda s: s[:1].lower() + s[1:] if s else ''

        base_name = controller.__name__
        view_name = base_name[:-len('Controller')] + view_posfix
        base_name = lower_first_char(base_name)

        self.main_controller.engine.rootContext().setContextProperty(base_name, c)
        self.main_controller.viewPushed.emit(view_name + '.qml')

        c.load_page(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        return invoke(*args, **kwargs)


def invoke(obj, func_name: str, value, var_type=QVariant):
    return QMetaObject.invokeMethod(obj, func_name, Q_ARG(var_type, value))


def main():
    from .Controllers.LoginController import LoginController
    try:
        print('Starting GUI')
        app = QApplication(sys.argv)
        engine = QQmlApplicationEngine()

        controller = Controller(engine)
        loginController = LoginController(controller)
        controller.active_controller_exit_point = loginController._unload

        engine.rootContext().setContextProperty("controller", controller)
        engine.rootContext().setContextProperty("loginController", loginController)
        engine.load(os.path.join(base_path, 'Views', "main.qml"))

        #component.loadUrl(QUrl(os.path.join(base_path, "main.qml")))

        def hide_all():
            print('hiding all root objects')
            for r in engine.rootObjects():
                r.hide()

        engine.quit.connect(hide_all)
        #engine.quit.connect(app.quit)
        app.exec_()
        print('application ended')
        app = None

    except Exception as ex:
        print(ex)
        pass


if __name__ == "__main__":
    main()

actions = {"start gui": {'run': main}}
