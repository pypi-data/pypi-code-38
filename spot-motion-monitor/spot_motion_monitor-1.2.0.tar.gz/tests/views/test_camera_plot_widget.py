#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from spot_motion_monitor.views.camera_plot_widget import CameraPlotWidget

class TestCameraPlotWidget():

    def test_parametersAfterConstruction(self, qtbot):
        cpw = CameraPlotWidget()
        cpw.show()
        qtbot.addWidget(cpw)
        assert cpw.image is not None
