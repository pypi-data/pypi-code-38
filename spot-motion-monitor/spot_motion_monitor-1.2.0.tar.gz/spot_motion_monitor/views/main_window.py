#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import cProfile
from datetime import datetime
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from spot_motion_monitor.controller.camera_controller import CameraController
from spot_motion_monitor.controller.data_controller import DataController
from spot_motion_monitor.controller.plot_ccd_controller import PlotCcdController
from spot_motion_monitor.controller.plot_centroid_controller import PlotCentroidController
from spot_motion_monitor.controller.plot_psd_controller import PlotPsdController
from spot_motion_monitor.utils import create_parser, DEFAULT_PSD_ARRAY_SIZE, readYamlFile
from spot_motion_monitor.views import CameraConfigurationDialog
from spot_motion_monitor.views import GeneralConfigurationDialog
from spot_motion_monitor.views import PlotConfigurationDialog
from spot_motion_monitor.views.forms import Ui_MainWindow
from spot_motion_monitor import __version__

__all__ = ['main']

class SpotMotionMonitor(QtWidgets.QMainWindow, Ui_MainWindow):

    """This is the main application class.

    Attributes
    ----------
    cameraActionGroup : QtWidgets.QActionGroup
        Allows the camera menu entries to be exclusive.
    cameraController : .CameraController
        An instance of the camera controller.
    dataController : .DataController
        An instance of the data controller.
    plotCentroidController : .PlotCentroidController
        An instance of the centroid (scatter and histograms) plot controller.
    plotController : .PlotCcdController
        An instance of the plot controller.
    plotPsdController : .PlotPsdController
        An instance of the Power Spectrum Distribution plot controller.
    """

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        self.cameraSwitched = False
        self.setupUi(self)
        self.setWindowTitle("Spot Motion Monitor")
        self.getProgramSettings()

        self.plotController = PlotCcdController(self.cameraPlot)
        self.cameraController = CameraController(self.cameraControl)
        self.dataController = DataController(self.cameraData)
        self.plotCentroidController = PlotCentroidController(self.centroidXPlot,
                                                             self.centroidYPlot,
                                                             self.scatterPlot)
        self.plotPsdController = PlotPsdController(self.psdWaterfallXPlot,
                                                   self.psdWaterfallYPlot,
                                                   self.psd1dXPlot,
                                                   self.psd1dYPlot)

        self.setupCameraMenu()

        self.setActionIcon(self.actionExit, "exit.svg", True)
        self.actionExit.setShortcut(QtGui.QKeySequence.Quit)

        self.cameraController.frameTimer.timeout.connect(self.acquireFrame)
        self.cameraController.offsetTimer.timeout.connect(self.updateOffset)
        self.cameraController.updater.displayStatus.connect(self.updateStatusBar)
        self.cameraController.updater.bufferSizeChanged.connect(self.handleBufferSizeChanged)
        self.cameraController.updater.roiFpsChanged.connect(self.handleRoiFpsChanged)
        self.cameraController.updater.cameraState.connect(self.updateApplicationForCameraState)
        self.cameraController.updater.acquireRoiState.connect(self.dataController.handleAcquireRoiStateChange)
        ccUpdArs = self.cameraController.updater.acquireRoiState.connect
        ccUpdArs(self.plotCentroidController.handleAcquireRoiStateChange)
        ccUpdArs(self.plotPsdController.handleAcquireRoiStateChange)
        self.plotController.updater.displayStatus.connect(self.updateStatusBar)
        self.dataController.updater.displayStatus.connect(self.updateStatusBar)
        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.about)
        self.actionPlotsConfig.triggered.connect(self.updatePlotConfiguration)
        self.actionCameraConfig.triggered.connect(self.updateCameraConfiguration)
        self.actionGeneralConfig.triggered.connect(self.updateGeneralConfiguration)

    def about(self):
        """This function presents the about dialog box.
        """
        about = QtWidgets.QMessageBox()
        about.setIconPixmap(QtGui.QPixmap(":smm_logo_sm.png"))
        about.setWindowTitle("About the Spot Motion Monitor")
        about.setStandardButtons(QtWidgets.QMessageBox.Ok)
        about.setInformativeText('''
                                 <b>Spot Motion Monitor</b> v{}
                                 <p>
                                 This application is the front-end for a system that
                                 monitors seeing within a telescope dome.
                                 </p>
                                 <br><br>
                                 Copyright 2018 LSST Systems Engineering
                                 '''.format(__version__))
        about.exec_()

    def acquireFrame(self):
        """Handle a camera CCD frame.
        """
        frame = self.cameraController.getFrame()
        cameraStatus = self.cameraController.currentStatus()
        self.dataController.passFrame(frame, cameraStatus)
        self.plotController.passFrame(frame, cameraStatus.showFrames)
        centroids = self.dataController.getCentroids(cameraStatus.isRoiMode)
        self.plotCentroidController.update(centroids[0], centroids[1])
        psdData = self.dataController.getPsd(cameraStatus.isRoiMode, cameraStatus.currentFps)
        bufferReady = psdData[0] is not None
        self.plotCentroidController.showScatterPlots(bufferReady)
        self.cameraController.showFrameStatus(bufferReady)
        self.dataController.showRoiInformation(bufferReady, cameraStatus)
        self.plotPsdController.update(psdData[0], psdData[1], psdData[2])
        self.dataController.writeDataToFile(psdData, cameraStatus.currentFps)

    def autoRunIfNecessary(self):
        """Start the program in ROI mode if requested.
        """
        self.cameraController.autoRun()

    def closeEvent(self, event):
        """Handle saving settings on shutdown.

        Parameters
        ----------
        event : QtCore.QEvent
            The close event instance.
        """
        settings = QtCore.QSettings()
        currentCamera = self.cameraActionGroup.checkedAction()
        if currentCamera is not None:
            cameraName = currentCamera.objectName()
            cameraValue = QtCore.QVariant(cameraName)
        else:
            cameraValue = QtCore.QVariant()
        settings.setValue('LastCamera', cameraValue)

        self.cameraController.shutdownCamera()

    def getProgramSettings(self):
        """Retrieve program settings.
        """
        settings = QtCore.QSettings()
        self.lastCamera = str(settings.value('LastCamera'))

    def handleBufferSizeChanged(self, newBufferSize):
        """Update the necessary controllers when the buffer size changes.

        Parameters
        ----------
        newBufferSize : int
            The new buffer size.
        """
        self.dataController.setBufferSize(newBufferSize)
        self.plotCentroidController.updateBufferSize(newBufferSize)

    def handleCameraSelection(self, checked):
        """Respond to a choice from the camera menu.

        Parameters
        ----------
        checked : bool
            If the current camera is selected.
        """
        name = self.sender().objectName()
        self.cameraController.setupCamera(name)
        self.dataController.setFrameChecks(*self.cameraController.getFrameChecks())
        bufferSize = self.dataController.getBufferSize()
        roiFps = self.cameraController.currentRoiFps()
        if self.cameraSwitched:
            self.plotCentroidController.updateBufferSize(bufferSize)
            self.plotCentroidController.updateRoiFps(roiFps)
        else:
            self.plotCentroidController.setup(bufferSize, roiFps)
            self.cameraSwitched = True
        self.plotPsdController.setup(DEFAULT_PSD_ARRAY_SIZE, bufferSize / roiFps)

    def handleConfig(self, options):
        """Call controller configuration functions.

        Parameters
        ----------
        options : Namespace
            The options from command-line arguments.
        """
        config = readYamlFile(options.config_file)
        if config is not None:
            config['file'] = options.config_file
        del options.config_file
        options.config = config
        self.dataController.setCommandLineConfig(options)
        self.cameraController.setCommandLineConfig(options)

    def handleRoiFpsChanged(self, newRoiFps):
        """Update the necessary controllers when the ROI FPS changes.

        Parameters
        ----------
        newRoiFps : int
            The new ROI FPS.
        """
        self.plotCentroidController.updateRoiFps(newRoiFps)
        bufferSize = self.dataController.getBufferSize()
        self.plotPsdController.updateTimeScale(bufferSize / newRoiFps)

    def setActionIcon(self, action, iconName, iconInMenu=False):
        """Setup the icon for the given action.

        Parameters
        ----------
        action : QAction
          A specific program action.
        iconName : str
          Name of the icon in the QRC file.
        iconInMenu : bool, optional
          Make the icon visible in the program menu.
        """
        action.setIcon(QtGui.QIcon(QtGui.QPixmap(':{}'.format(iconName))))
        action.setIconVisibleInMenu(iconInMenu)

    def setupCameraMenu(self):
        """Add the available cameras to the menu.
        """
        cameraList = self.cameraController.getAvailableCameras()
        self.cameraActionGroup = QtWidgets.QActionGroup(self)
        index = 0
        for i, cameraName in enumerate(cameraList):
            if cameraName == 'Gaussian':
                index = i
            cameraAction = QtWidgets.QAction(cameraName, self)
            self.cameraActionGroup.addAction(cameraAction)
            cameraAction.setObjectName('{}Camera'.format(cameraName))
            cameraAction.triggered.connect(self.handleCameraSelection)
            cameraAction.setCheckable(True)
            self.menuCamera.addAction(cameraAction)
        action = None
        if self.lastCamera != 'None':
            for menuAction in self.menuCamera.actions():
                if menuAction.objectName() == self.lastCamera:
                    action = menuAction
                    break
        else:
            # Setup the Gaussian camera.
            action = self.menuCamera.actions()[index]
        action.setChecked(True)
        action.trigger()

    def updateApplicationForCameraState(self, state):
        """Update any application UI elements based on camera state.

        Parameters
        ----------
        state : bool
            True is camera is started, False is stopped.
        """
        self.menuCamera.setEnabled(not state)
        self.actionCameraConfig.setEnabled(not state)

    def updateCameraConfiguration(self):
        """This function handles camera configuration.

        The camera configuration dialog is shown when the menu action is
        triggered. If dialog is accepted (OK button pressed), then the
        configuration is read from the tab and applied to the current via the
        camera controller.
        """
        currentCamera = self.cameraActionGroup.checkedAction()
        if currentCamera is None:
            return
        cameraName = currentCamera.objectName()
        cameraConfigDialog = CameraConfigurationDialog(cameraName)
        currentConfig = self.cameraController.getCameraConfiguration()
        cameraConfigDialog.setCameraConfiguration(currentConfig)
        if cameraConfigDialog.exec_():
            config = cameraConfigDialog.getCameraConfiguration()
            self.cameraController.setCameraConfiguration(config)

    def updateGeneralConfiguration(self):
        """This function handles general configuration.

        The configuration is centered on the data structures used for the
        calculations.
        """
        generalConfigDialog = GeneralConfigurationDialog()
        currentDataConfig = self.dataController.getDataConfiguration()
        generalConfigDialog.setConfiguration(currentDataConfig)
        if generalConfigDialog.exec_():
            newDataConfig = generalConfigDialog.getConfiguration()
            self.dataController.setDataConfiguration(newDataConfig)

    def updateOffset(self):
        """This function updates the camera offsets.
        """
        frame = self.cameraController.getUpdateFrame()
        info = self.dataController.getCentroidForUpdate(frame)
        self.cameraController.updateCameraOffset(info.centerX, info.centerY)

    def updatePlotConfiguration(self):
        """This function handles plot configuration.

        The plot configuration dialog is shown when the menu action is
        triggered. If dialog is accepted (OK button pressed), then the
        configuration is read from the tabs and applied to the plots via the
        respective controllers.
        """
        plotConfigDialog = PlotConfigurationDialog()
        plotConfigDialog.setMinimumSize(300, 500)
        currentCentroidConfig = self.plotCentroidController.getPlotConfiguration()
        currentPsdConfig = self.plotPsdController.getPlotConfiguration()
        plotConfigDialog.setPlotConfiguration(currentCentroidConfig, currentPsdConfig)
        if plotConfigDialog.exec_():
            newCentroidConfig, newPsdConfig = plotConfigDialog.getPlotConfiguration()
            self.plotCentroidController.setPlotConfiguration(newCentroidConfig)
            self.plotPsdController.setPlotConfiguration(newPsdConfig)

    def updateStatusBar(self, message, timeout):
        """This function updates the application status bar.

        Parameters
        ----------
        message : str
            The text to display in the status bar.
        timeout : int
            The time (in milliseconds) for the text to remain visible.
        """
        self.statusbar.showMessage(message, timeout)


def launch(opts):
    """This creates the application and launches the program.

    Parameters
    ----------
    opts : Namespace
        The parsed command-line options.
    """
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName("LSST-Systems-Engineering")
    app.setOrganizationDomain("lsst.org")
    app.setApplicationName("Spot Motion Monitor")
    form = SpotMotionMonitor()
    form.handleConfig(opts)
    form.show()
    form.autoRunIfNecessary()
    app.exec_()


def main():
    """This is the entrance point of the program.
    """
    parser = create_parser()
    args = parser.parse_args()
    if args.profile:
        profileFile = 'smm_prof_{}.dat'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
        cProfile.runctx('launch(args)', {'launch': launch, 'args': args}, {}, filename=profileFile)
    else:
        launch(args)
