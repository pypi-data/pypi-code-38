#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
#from pyqtgraph import ImageView, PlotItem

from spot_motion_monitor.controller.plot_ccd_controller import PlotCcdController
from spot_motion_monitor.views.camera_plot_widget import CameraPlotWidget

class TestPlotCcdController():

    def test_parametersAfterConstruction(self, qtbot):
        cpw = CameraPlotWidget()
        qtbot.addWidget(cpw)
        pc = PlotCcdController(cpw)
        assert pc.cameraPlotWidget is not None
        assert pc.updater is not None

    def test_passFrame(self, qtbot):
        cpw = CameraPlotWidget()
        cpw.show()
        qtbot.addWidget(cpw)
        pc = PlotCcdController(cpw)
        frame = np.ones((3, 5))
        pc.passFrame(frame, True)
        pc.cameraPlotWidget.image.shape = (3, 5)

    def test_passFrameWithNoShowFrames(self, qtbot, mocker):
        cpw = CameraPlotWidget()
        cpw.show()
        qtbot.addWidget(cpw)
        pc = PlotCcdController(cpw)
        frame = np.ones((3, 5))
        mockSetImage = mocker.patch.object(pc.cameraPlotWidget.image, 'setImage')
        pc.passFrame(frame, False)
        assert mockSetImage.call_count == 0

    def test_passFrameWithNone(self, qtbot, mocker):
        cpw = CameraPlotWidget()
        cpw.show()
        qtbot.addWidget(cpw)
        pc = PlotCcdController(cpw)
        cpwImage = mocker.patch.object(cpw.image, 'setImage')
        pc.passFrame(None, True)
        assert cpwImage.call_count == 0
