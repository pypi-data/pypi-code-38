'''SplotPlotLP class definition'''

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, AdaptiveTicker, \
    NumeralTickFormatter
from bokeh.models.layouts import Column, Row
from bokeh.models.callbacks import CustomJS
from bokeh.models.tools import TapTool
from bokeh.models.widgets.markups import Paragraph

from bokeh.core.properties import Instance, String

from .SpotPlot import SpotPlot

from .get_common_kwargs import get_common_kwargs


class SpotPlotLP(Row):

    '''
    A SpotPlot and a line plot of the data against z at the x and y coordinates
    linked to a custom tap tool.
    '''

    __view_model__ = "Row"
    __subtype__ = "SpotPlotLP"

    spplot = Instance(SpotPlot)
    lpcon = Instance(Column)
    lplot = Instance(Plot)
    lpds = Instance(ColumnDataSource)
    cmxlab = String
    cmylab = String
    tstr = String

    def __init__(self, x, y, z, dm, **kwargs):

        '''
        All init arguments same as for SpotPlot except for additional ones:
        spheight and spwidth correspond to height and width in SpotPlot.
        lpheight and lpwidth: line plot height and width (pixels).
        revz: reverse z axis in line plot if True.
        '''

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        spheight = kwargs.get('spheight', 575)
        spwidth = kwargs.get('spwidth', 500)
        lpheight = kwargs.get('lpheight', 500)
        lpwidth = kwargs.get('lpwidth', 300)
        revz = kwargs.get('revz', False)

        super().__init__()

        xi = round(x.size/2)
        self.lpds = ColumnDataSource(data={'x': dm[:, xi], 'y': z, 'dm': dm})

        jscode = '''
        var inds = cb_obj.get('selected')['1d'].indices;
        if (inds.length > 0) {
            var ind = inds[0];
            var data = source.data;
            var x = data['x'];
            var y = data['y'];
            dm = data['dm'];
            var skip = dm.length/y.length;
            for (i = 0; i < y.length; i++) {
                x[i] = dm[ind + i*skip];
            }
            source.change.emit();
        }
        '''

        update_lp = CustomJS(args={'source': self.lpds}, code=jscode)
        ttool = TapTool(callback=update_lp)

        self.spplot = SpotPlot(x, y, z, dm, palette=palette, cfile=cfile,
                               xlab=xlab, ylab=ylab, zlab=zlab, dmlab=dmlab,
                               height=spheight, width=spwidth, rmin=rmin,
                               rmax=rmax, xran=xran, yran=yran, ttool=ttool)

        self.lplot = Figure(x_axis_label=dmlab, y_axis_label=zlab,
                            plot_height=lpheight, plot_width=lpwidth,
                            tools=["reset,pan,wheel_zoom,box_zoom,save"],
                            toolbar_location='right')

        self.lplot.line('x', 'y', source=self.lpds, line_color='blue',
                        line_width=2, line_alpha=1)

        self.lplot.y_range.start = self.lpds.data['y'].min()
        self.lplot.y_range.end = self.lpds.data['y'].max()
        if revz:
            self.lplot.y_range.start, self.lplot.y_range.end = \
                self.lplot.y_range.end, self.lplot.y_range.start
        if (rmin is not None) and (rmax is not None):
            self.lplot.x_range.start = rmin
            self.lplot.x_range.end = rmax

        self.lplot.xaxis.axis_label_text_font = 'garamond'
        self.lplot.xaxis.axis_label_text_font_size = '10pt'
        self.lplot.xaxis.axis_label_text_font_style = 'bold'

        self.lplot.xaxis[0].ticker = AdaptiveTicker(desired_num_ticks=4)
        self.lplot.xaxis[0].formatter = NumeralTickFormatter(format="0.00")

        self.lplot.yaxis.axis_label_text_font = 'garamond'
        self.lplot.yaxis.axis_label_text_font_size = '10pt'
        self.lplot.yaxis.axis_label_text_font_style = 'bold'

        self.lpcon = Column(self.lplot, Paragraph(text=''))

        self.children.append(self.spplot)
        self.children.append(self.lpcon)
