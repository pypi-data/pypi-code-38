'''SplotPlotSlider class definition'''

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

from .SpotPlot import SpotPlot

from .get_common_kwargs import get_common_kwargs


class SpotPlotSlider(Column):

    '''
    A SpotPlot with a slider linked to the z coordinate
    (i.e. the row being displayed).
    '''

    splot = Instance(SpotPlot)
    zslider = Instance(Slider)

    __view_model__ = "Column"
    __subtype__ = "SpotPlotSlider"

    def __init__(self, x, y, z, dm, **kwargs):

        '''
        All init arguments same as for SpotPlot.
        '''

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        height = kwargs.get('height', 575)
        width = kwargs.get('width', 500)

        super().__init__()

        self.height = height
        self.width = int(width*1.1)

        self.splot = SpotPlot(x, y, z, dm, palette=palette, cfile=cfile,
                              xlab=xlab, ylab=ylab, zlab=zlab, dmlab=dmlab,
                              height=height, width=width, rmin=rmin,
                              rmax=rmax, xran=xran, yran=yran)

        self.zslider = Slider(title='z index', start=0, end=z.size-1,
                              step=1, value=0, orientation='horizontal')

        self.zslider.on_change('value', self.splot.input_change)

        self.children.append(WidgetBox(self.zslider, width=self.width))
        self.children.append(self.splot)
