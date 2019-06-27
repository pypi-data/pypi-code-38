'''SplotPlotLPSlider class definition'''

from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column, WidgetBox

from bokeh.core.properties import Instance

from .SpotPlotLP import SpotPlotLP

from .get_common_kwargs import get_common_kwargs


class SpotPlotLPSlider(Column):

    '''
    A SpotPlotLP with a slider linked to the z coordinate
    (i.e. the row being displayed).
    '''

    __view_model__ = "Column"
    __subtype__ = "SpotPlotLPSlider"

    splotlp = Instance(SpotPlotLP)
    zslider = Instance(Slider)

    def __init__(self, x, y, z, dm, **kwargs):

        '''
        All init arguments same as for SpotPlotLP.
        '''

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        spheight = kwargs.get('spheight', 575)
        spwidth = kwargs.get('spwidth', 500)
        lpheight = kwargs.get('lpheight', 500)
        lpwidth = kwargs.get('lpwidth', 300)
        revz = kwargs.get('revz', False)

        super(SpotPlotLPSlider, self).__init__()

        self.height = spheight
        self.width = int((spwidth + lpwidth)*1.1)

        self.splotlp = SpotPlotLP(x, y, z, dm, palette=palette, cfile=cfile,
                                  xlab=xlab, ylab=ylab, zlab=zlab, dmlab=dmlab,
                                  spheight=spheight, spwidth=spwidth,
                                  lpheight=lpheight, lpwidth=lpwidth,
                                  rmin=rmin, rmax=rmax, xran=xran, yran=yran,
                                  revz=revz)

        self.zslider = Slider(title=zlab + ' index', start=0, end=z.size-1,
                              step=1, value=0, orientation='horizontal')

        self.zslider.on_change('value', self.splotlp.spplot.input_change)

        self.children.append(WidgetBox(self.zslider, width=self.width))
        self.children.append(self.splotlp)
