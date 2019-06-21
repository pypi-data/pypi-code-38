#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtGui import QDoubleValidator

from spot_motion_monitor.views import BaseConfigTab
from spot_motion_monitor.views.forms.ui_data_config import Ui_DataConfigForm

__all__ = ['DataConfigTab']

class DataConfigTab(BaseConfigTab, Ui_DataConfigForm):
    """Class that handles the data configuration tab.

    Attributes
    ----------
    name : str
        The name for the tab widget.
    """

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.name = 'Data'
        self.pixelScaleLineEdit.setValidator(QDoubleValidator(0.0, 1.0e200, 5))
        self.pixelScaleLineEdit.textChanged.connect(self.validateInput)

    def getConfiguration(self):
        """Get the configuration parameter's from the tab's widgets.

        Returns
        -------
        dict
            The current set of configuration parameters.
        """
        config = {}
        config['pixelScale'] = float(self.pixelScaleLineEdit.text())
        return config

    def setConfiguration(self, config):
        """Set the configuration parameters into the tab's widgets.

        Parameters
        ----------
        config : dict
            The current set of configuration parameters.
        """
        self.pixelScaleLineEdit.setText(str(config['pixelScale']))
