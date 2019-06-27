# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO Engineering, 2019
license   GPL v3.0+
brief     My QComboBox widget.
"""

from PyQt5.QtCore import pyqtSignal, QEvent
from PyQt5.QtGui import QComboBox


class MyQComboBox(QComboBox):
    """MyQComboBox class, add generation of enabled change signals.
    """

    enabled_changed = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        """Constructor.
        :returns: None
        """
        super(MyQComboBox, self).__init__(*args, **kwargs)

    def changeEvent(self, event):
        """Overloaded method: add emmission of signal "enabled_changed" when
        event emited is of type "EnabledChange".
        :param event: intercepted event (QEvent)
        :returns: None
        """
        super(MyQComboBox, self).changeEvent(event)
        if event == QEvent.EnabledChange:
            self.enabled_changed.emit(self.isEnabled)
