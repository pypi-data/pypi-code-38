# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO ENGINEERING, 2019
license   GPL v3.0+
date      2015-02-13
brief     My QLabel widget, add generation of signals when user click on label.
"""


from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QLabel


class MyQLabel(QLabel):
    """MyQLabel class, add generation of left_pressed and right_pressed signals.
    """

    left_pressed = pyqtSignal()
    middle_pressed = pyqtSignal()
    right_pressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        """Constructor.
        :returns: None
        """
        super(MyQLabel, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event):
        """Overloaded method: add emmission of signal "left_pressed" and
        "right_pressed" when event emited is of type "EnabledChange".
        :param event: intercepted event (QMouseEvent)
        :returns: None
        """
        super(MyQLabel, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.left_pressed.emit()
        elif event.button() == Qt.RightButton:
            self.right_pressed.emit()
        elif event.button() == Qt.MidButton:
            self.middle_pressed.emit()
