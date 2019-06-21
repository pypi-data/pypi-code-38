"""Summary
"""
#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QTabWidget

__all__ = ['BaseConfigTab']

class BaseConfigTab(QTabWidget):
    """Class that sets up the main API for configuration tabs.

    Attributes
    ----------
    hasValidInput : pyqtSignal
        Signal emitted when checking for valid input.
    name : str
        The name for the tab widget.
    """

    hasValidInput = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.name = 'Base'

    def getConfiguration(self):
        """Get the configuration parameter's from the tab's widgets.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def setConfiguration(self, config):
        """Set the configuration parameters into the tab's widgets.

        Parameters
        ----------
        config : dict
            The current set of configuration parameters.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError

    def validateInput(self):
        """Check if a line edit has valid input.

        This function checks a line edit widget that has a validator attached
        and looks for valid input. If valid input is not found, the text color
        is changed to blue and a False value is sent in the signal.
        """
        palette = QPalette()
        validInput = self.sender().hasAcceptableInput()
        if validInput:
            palette.setColor(QPalette.Text, Qt.black)
        else:
            palette.setColor(QPalette.Text, Qt.blue)
        self.sender().setPalette(palette)
        self.hasValidInput.emit(validInput)
