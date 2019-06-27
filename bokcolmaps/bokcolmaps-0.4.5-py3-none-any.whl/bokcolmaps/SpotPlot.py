'''SplotPlot class definition'''

import numpy

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, Plot, ColorBar
from bokeh.models.mappers import LinearColorMapper
from bokeh.models.layouts import Column

from bokeh.core.properties import Instance, String, Int, Float, Bool

from .get_common_kwargs import get_common_kwargs
from .generate_colourbar import generate_colourbar
from .read_colourmap import read_colourmap
from .get_min_max import get_min_max


class SpotPlot(Column):

    '''
    Like a scatter plot but with the points colour mapped with a
    user-defined colour scale.
    '''

    __view_model__ = "Column"
    __subtype__ = "SpotPlot"

    __sizing_mode__ = 'stretch_both'

    plot = Instance(Plot)
    cbar = Instance(ColorBar)

    datasrc = Instance(ColumnDataSource)
    coldatasrc = Instance(ColumnDataSource)
    cvals = Instance(ColumnDataSource)
    cmap = Instance(LinearColorMapper)

    title_root = String
    zlab = String
    bg_col = String
    nan_col = String
    sp_size = Int
    rmin = Float
    rmax = Float
    autoscale = Bool
    cbdelta = Float

    def __init__(self, x, y, z, dm, **kwargs):

        '''
        x and y (same length) give the spot locations, z is the
        (common) z axis. All are 1D NumPy arrays.
        dm is a 2D NumPy array of the data for display, dimensions
        z.size by x.size (or y.size).
        Supply a bokeh palette name or a file of RGBA floats;
        the file will be used if provided.
        xlab,ylab,zlab,dmlab: labels for the axes and data.
        height and width for the plot are in pixels.
        rmin and rmax are fixed limits for the colour scale
        (i.e. it won't autoscale if either of these is not None).
        xran and yran: ranges for the x and y axes
        (e.g. to link to another plot).
        ttool: custom tap tool passed in from SpotPlotLP class.
        '''

        palette, cfile, xlab, ylab, zlab,\
            dmlab, rmin, rmax, xran, yran = get_common_kwargs(**kwargs)

        height = kwargs.get('height', 575)
        width = kwargs.get('width', 500)
        ttool = kwargs.get('ttool', None)

        super().__init__()

        self.cbdelta = 0.01  # Min colourbar range (used if values are equal)

        self.title_root = dmlab
        self.zlab = zlab

        self.rmin = rmin
        self.rmax = rmax
        self.autoscale = True
        if (self.rmin is not None) & (self.rmax is not None):
            self.autoscale = False

        if z.size > 1:  # Default to first 'slice'
            d = dm[0]
        else:
            d = dm

        if self.autoscale:
            min_val, max_val = get_min_max(d, self.cbdelta)
        else:
            min_val = self.rmin
            max_val = self.rmax

        if cfile is not None:
            self.read_cmap(cfile)
            self.cmap = LinearColorMapper(palette=self.cvals.data['colours'])
        else:
            self.cmap = LinearColorMapper(palette=palette)
            self.cvals = ColumnDataSource(data={'colours': self.cmap.palette})
        self.cmap.low = min_val
        self.cmap.high = max_val

        self.bg_col = 'black'
        self.nan_col = 'grey'
        self.sp_size = int(min(height, width)/25)

        cols = [self.nan_col]*d.size  # Initially empty
        self.datasrc = ColumnDataSource(data={'z': [z], 'd': [d], 'dm': [dm]})
        self.coldatasrc = ColumnDataSource(data={'x': x, 'y': y, 'cols': cols})

        ptools = ["reset,pan,wheel_zoom,box_zoom,save"]
        if ttool is not None:
            ptools.append(ttool)

        # Default to entire range unless externally controlled
        if xran is None:
            xran = [x.min(), x.max()]
        if yran is None:
            yran = [y.min(), y.max()]

        self.plot = Figure(x_axis_label=xlab, y_axis_label=ylab,
                           x_range=xran, y_range=yran,
                           plot_height=height, plot_width=width,
                           background_fill_color=self.bg_col,
                           tools=ptools, toolbar_location='right')

        self.plot.circle('x', 'y', size=self.sp_size, color='cols',
                         source=self.coldatasrc,
                         nonselection_fill_color='cols',
                         selection_fill_color='cols',
                         nonselection_fill_alpha=1, selection_fill_alpha=1,
                         nonselection_line_alpha=0, selection_line_alpha=1,
                         nonselection_line_color='cols',
                         selection_line_color='white', line_width=5)

        self.update_title(0)

        self.plot.title.text_font = 'garamond'
        self.plot.title.text_font_size = '12pt'
        self.plot.title.text_font_style = 'bold'
        self.plot.title.align = 'center'

        self.plot.xaxis.axis_label_text_font = 'garamond'
        self.plot.xaxis.axis_label_text_font_size = '10pt'
        self.plot.xaxis.axis_label_text_font_style = 'bold'

        self.plot.yaxis.axis_label_text_font = 'garamond'
        self.plot.yaxis.axis_label_text_font_size = '10pt'
        self.plot.yaxis.axis_label_text_font_style = 'bold'

        self.update_colours()

        self.generate_colorbar(cbarwidth=round(width/20))

        self.children.append(self.plot)

    def generate_colorbar(self, cbarwidth=25):
        '''
        Generate the colourbar
        '''

        self.cbar = generate_colourbar(self.cmap, cbarwidth)
        self.plot.add_layout(self.cbar, 'below')

    def read_cmap(self, fname):

        '''
        Read in the colour scale.
        '''

        self.cvals = read_colourmap(fname)

    def changed(self, zind):

        '''
        Change the row of dm being displayed (i.e. a different value of z)
        '''

        if (len(self.datasrc.data['dm'][0].shape) > 1) and \
           (zind >= 0) and (zind < self.datasrc.data['dm'][0].shape[0]):
            data = self.datasrc.data
            newdata = data
            d = data['dm'][0][zind]
            newdata['d'] = [d]
            self.datasrc.trigger('data', data, newdata)

    def update_cbar(self):

        '''
        Update the colour scale (needed when the data for display changes).
        '''

        if self.autoscale:
            d = self.datasrc.data['d'][0]
            min_val, max_val = get_min_max(d, self.cbdelta)
            self.cmap.low = min_val
            self.cmap.high = max_val

    def update_title(self, zind):

        if self.datasrc.data['z'][0].size > 1:
            val = self.datasrc.data['z'][0][zind]
        else:
            val = self.datasrc.data['z'][0]
        self.plot.title.text = self.title_root + ', ' + \
            self.zlab + ' = ' + str(val)

    def input_change(self, attrname, old, new):

        '''
        Callback for use with e.g. sliders.
        '''

        self.convert_data()
        self.changed(new)
        self.update_cbar()
        self.update_colours()
        self.update_title(new)

    def update_colours(self):

        '''
        Update the spot colours (needed when the data for display changes).
        '''

        colset = self.cvals.data['colours']
        ncols = len(colset)

        d = self.datasrc.data['d'][0]

        data = self.coldatasrc.data
        newdata = data
        cols = data['cols']

        min_val = self.cmap.low
        max_val = self.cmap.high

        for s in range(d.size):
            if numpy.isfinite(d[s]):
                cind = int(round(ncols*(d[s] - min_val)/(max_val - min_val)))
                if cind < 0:
                    cind = 0
                if cind >= ncols:
                    cind = ncols - 1
                cols[s] = colset[cind]
            else:
                cols[s] = self.nan_col

        newdata['cols'] = cols
        self.coldatasrc.trigger('data', data, newdata)

    def convert_data(self):

        '''
        NumPy arrays sometimes not deserialised from lists so need to check.
        '''

        data = self.datasrc.data
        newdata = data
        for k in ['z', 'd', 'dm']:
            if type(newdata[k][0]) is list:
                newdata[k][0] = numpy.array(newdata[k][0])
