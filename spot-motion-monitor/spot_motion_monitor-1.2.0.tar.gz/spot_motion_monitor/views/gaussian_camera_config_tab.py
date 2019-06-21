#------------------------------------------------------------------------------
# Copyright (c) 2018-2019 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtGui import QDoubleValidator, QIntValidator

import spot_motion_monitor.utils as utils
from spot_motion_monitor.views import BaseConfigTab
from spot_motion_monitor.views.forms.ui_gaussian_camera_config import Ui_GaussianCameraConfigForm

__all__ = ['GaussianCameraConfigTab']

class GaussianCameraConfigTab(BaseConfigTab, Ui_GaussianCameraConfigForm):
    """Class that handles the Gaussian camera configuration tab.

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
        self.name = 'Gaussian'
        self.roiSizeLineEdit.setValidator(QIntValidator(20, 200))
        self.xAmpLineEdit.setValidator(QIntValidator(1, 20))
        self.xFreqLineEdit.setValidator(QDoubleValidator(0.1, 100.0, 1, self))
        self.yAmpLineEdit.setValidator(QIntValidator(1, 20))
        self.yFreqLineEdit.setValidator(QDoubleValidator(0.1, 100.0, 1))
        self.spotOscillationCheckBox.toggled.connect(self.changeGroupBoxState)
        self.roiSizeLineEdit.textChanged.connect(self.validateInput)
        self.xAmpLineEdit.textChanged.connect(self.validateInput)
        self.xFreqLineEdit.textChanged.connect(self.validateInput)
        self.yAmpLineEdit.textChanged.connect(self.validateInput)
        self.yFreqLineEdit.textChanged.connect(self.validateInput)

    def changeGroupBoxState(self, checked):
        """Adjust the oscillation parameters group box based on check box
           state.

        Parameters
        ----------
        checked : bool
            The current state of the check box.
        """
        self.spotOscillationGroupBox.setEnabled(checked)

    def getConfiguration(self):
        """Get the configuration parameter's from the tab's widgets.

        Returns
        -------
        dict
            The current set of configuration parameters.
        """
        config = {}
        config['roiSize'] = int(self.roiSizeLineEdit.text())
        config['doSpotOscillation'] = utils.checkStateToBool(self.spotOscillationCheckBox.checkState())
        if config['doSpotOscillation']:
            xAmp = utils.defaultToNoneOrValue(self.xAmpLineEdit.text())
            config['xAmplitude'] = utils.convertValueOrNone(xAmp)
            xFreq = utils.defaultToNoneOrValue(self.xFreqLineEdit.text())
            config['xFrequency'] = utils.convertValueOrNone(xFreq, convert=float)
            yAmp = utils.defaultToNoneOrValue(self.yAmpLineEdit.text())
            config['yAmplitude'] = utils.convertValueOrNone(yAmp)
            yFreq = utils.defaultToNoneOrValue(self.yFreqLineEdit.text())
            config['yFrequency'] = utils.convertValueOrNone(yFreq, convert=float)
        print(config)
        return config

    def setConfiguration(self, config):
        """Set the configuration parameters into the tab's widgets.

        Parameters
        ----------
        config : dict
            The current set of configuration parameters.
        """
        self.roiSizeLineEdit.setText(str(config['roiSize']))
        self.spotOscillationCheckBox.setCheckState(utils.boolToCheckState(config['doSpotOscillation']))
        self.xAmpLineEdit.setText(str(config['xAmplitude']))
        self.xFreqLineEdit.setText(str(config['xFrequency']))
        self.yAmpLineEdit.setText(str(config['yAmplitude']))
        self.yFreqLineEdit.setText(str(config['yFrequency']))
