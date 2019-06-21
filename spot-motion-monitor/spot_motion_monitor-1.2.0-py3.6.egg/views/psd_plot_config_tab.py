#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

import spot_motion_monitor.utils as utils
from spot_motion_monitor.views import BaseConfigTab
from spot_motion_monitor.views.forms.ui_psd_plots_config import Ui_PsdPlotConfigForm

__all__ = ['PsdPlotConfigTab']

class PsdPlotConfigTab(BaseConfigTab, Ui_PsdPlotConfigForm):
    """Class that handles the Power Spectrum Distribution plot configuration
       tab.

    Attributes
    ----------
    name : str
        The name for the tab widget.
    """

    def __init__(self, parent=None):
        """Summary

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.name = 'PSD'
        self.waterfallNumBinsLineEdit.setValidator(QIntValidator(1, 1000))
        self.waterfallNumBinsLineEdit.textChanged.connect(self.validateInput)

        self.waterfallColorMapComboBox.addItems(utils.COLORMAPS)

        self.autoscaleX1dCheckBox.stateChanged.connect(self.handleAutoscaleChange)
        self.autoscaleY1dCheckBox.stateChanged.connect(self.handleAutoscaleChange)

    def getConfiguration(self):
        """Get the current configuration parameters from the tab's widgets.

        Returns
        -------
        dict
            The current set of configuration parameters.
        """
        config = {}
        config['waterfall'] = {}
        config['waterfall']['numBins'] = int(self.waterfallNumBinsLineEdit.text())
        config['waterfall']['colorMap'] = self.waterfallColorMapComboBox.currentText()
        config['xPSD'] = {}
        xAutoscale = utils.checkStateToBool(self.autoscaleX1dCheckBox.checkState())
        config['xPSD']['autoscale'] = xAutoscale
        if not xAutoscale:
            xMax = utils.defaultToNoneOrValue(self.x1dMaximumLineEdit.text())
            config['xPSD']['maximum'] = xMax if xMax is None else float(xMax)
        config['yPSD'] = {}
        yAutoscale = utils.checkStateToBool(self.autoscaleY1dCheckBox.checkState())
        config['yPSD']['autoscale'] = yAutoscale
        if not yAutoscale:
            yMax = utils.defaultToNoneOrValue(self.y1dMaximumLineEdit.text())
            config['yPSD']['maximum'] = yMax if yMax is None else float(yMax)
        return config

    def handleAutoscaleChange(self, currentState):
        """Change state of line edits based on autoscale state.

        Parameters
        ----------
        currentState : int
            The current autoscale state.
        """
        axis = self.sender().objectName().split('autoscale')[-1][0].lower()
        if currentState == Qt.Checked:
            getattr(self, '{}1dMaximumLabel'.format(axis)).setEnabled(False)
            getattr(self, '{}1dMaximumLineEdit'.format(axis)).setEnabled(False)
        else:
            getattr(self, '{}1dMaximumLabel'.format(axis)).setEnabled(True)
            getattr(self, '{}1dMaximumLineEdit'.format(axis)).setEnabled(True)

    def setConfiguration(self, config):
        """Set the configuration parameters into the tab's widgets.

        Parameters
        ----------
        config : dict
            The current set of configuration parameters.
        """
        self.waterfallNumBinsLineEdit.setText(str(config['waterfall']['numBins']))
        value = utils.noneToDefaultOrValue(config['waterfall']['colorMap'])
        self.waterfallColorMapComboBox.setCurrentText(value)
        self.autoscaleX1dCheckBox.setCheckState(utils.boolToCheckState(config['xPSD']['autoscale']))
        self.x1dMaximumLineEdit.setText(str(utils.noneToDefaultOrValue(config['xPSD']['maximum'])))
        self.autoscaleY1dCheckBox.setCheckState(utils.boolToCheckState(config['yPSD']['autoscale']))
        self.y1dMaximumLineEdit.setText(str(utils.noneToDefaultOrValue(config['yPSD']['maximum'])))
