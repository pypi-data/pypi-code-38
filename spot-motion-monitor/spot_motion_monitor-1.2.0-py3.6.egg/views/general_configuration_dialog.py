#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.views import BaseConfigurationDialog, DataConfigTab

__all__ = ['GeneralConfigurationDialog']

class GeneralConfigurationDialog(BaseConfigurationDialog):
    """Class that generates the dialog for handling general data configuration.

    Attributes
    ----------
    dataConfigTab : DataConfigTab
        Instance of the data configuration tab.
    """

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.dataConfigTab = DataConfigTab()

        self.tabWidget.addTab(self.dataConfigTab, self.dataConfigTab.name)
        self.dataConfigTab.hasValidInput.connect(self.inputFromTabsValid)

    def getConfiguration(self):
        """Get the current data configuration from the tab.

        Returns
        -------
        dict
            The current set of configuration parameters.
        """
        config = self.dataConfigTab.getConfiguration()
        return config

    def setConfiguration(self, config):
        """Set the current data configuration in the tab.

        Parameters
        ----------
        config : dict
          The current set of configuration parameters.
        """
        self.dataConfigTab.setConfiguration(config)
