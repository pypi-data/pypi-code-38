#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import spot_motion_monitor.views
from spot_motion_monitor.views import BaseConfigurationDialog

__all__ = ['CameraConfigurationDialog']

class CameraConfigurationDialog(BaseConfigurationDialog):
    """Class that generates the dialog for handling camera configuration.

    Attributes
    ----------
    cameraConfigTab : GaussianCameraConfigTab or VimbaCameraConfigTab
        Instance of the appropriate camera configuration tab.
    """

    def __init__(self, camera, parent=None):
        """Initialize the class.

        Parameters
        ----------
        camera : str
            The name of the camera to get the configuration tab for.
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.cameraConfigTab = getattr(spot_motion_monitor.views, '{}ConfigTab'.format(camera))()

        self.tabWidget.addTab(self.cameraConfigTab, self.cameraConfigTab.name)
        self.cameraConfigTab.hasValidInput.connect(self.inputFromTabsValid)

    def getCameraConfiguration(self):
        """Get the current camera configuration from the tab.

        Returns
        -------
        dict
            The current set of configuration parameters.
        """
        config = self.cameraConfigTab.getConfiguration()
        return config

    def setCameraConfiguration(self, config):
        """Set the current camera configuration in the tab.

        Parameters
        ----------
        config : dict
          The current set of configuration parameters.
        """
        self.cameraConfigTab.setConfiguration(config)
