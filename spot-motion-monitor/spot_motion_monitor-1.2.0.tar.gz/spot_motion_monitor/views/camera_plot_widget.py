#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
from pyqtgraph import GraphicsLayoutWidget, ImageItem

__all__ = ['CameraPlotWidget']

class CameraPlotWidget(GraphicsLayoutWidget):

    """This class manages and displays the camera CCD frame.

    Attributes
    ----------
    image : numpy.array
        The data frame to display.
    """

    def __init__(self, parent=None):
        """Initialize the class.

        Parameters
        ----------
        parent : None, optional
            Top-level widget.
        """
        super().__init__(parent)
        p1 = self.addPlot()
        p1.setAspectLocked(True)
        self.image = ImageItem()
        self.image.setOpts(axisOrder='row-major')
        p1.addItem(self.image)
