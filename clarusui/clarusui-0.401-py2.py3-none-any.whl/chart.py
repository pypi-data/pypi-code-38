"""Wrappers for useful plotly.py charts."""
from abc import ABCMeta, abstractmethod
import numpy as np
import plotly.graph_objs as graphs
import plotly.offline as py
import plotly.figure_factory as ff
from clarusui.gridvisualisationelement import GridViz
from clarusui import utils
from clarusui import templates as tmp

class Chart(GridViz):

    __metaclass__ = ABCMeta

    def __init__(self, response, **options):
        self.layout = dict()
        self.xoptions = dict()
        self.yoptions = dict()
        self.yoptions2 = dict()
        self.set_height()
        #self._colours = None
        super(Chart, self).__init__(response, **options)

    def set_height(self, height=450):
        if height is not None:
            self.layout.update({'height' : height, 'autosize' : True})

    def set_font(self, style):
        font = dict()
        if style is not None:
            font['color'] = style.font_colour
            font['family'] = style.font_family
            font['size'] = 18
            self.layout['font'] = font
        super(Chart, self).set_font(style)

    def _get_layout(self):
        return self.layout

    def _get_xoptions(self):
        return self.xoptions

    def _get_yoptions(self):
        return self.yoptions

    def set_layout(self, layout):
        self.layout = layout

    def set_xoptions(self, options):
        self.xoptions = options

    def set_yoptions(self, options):
        self.yoptions = options

    def add_xoptions(self, options):
        self._get_xoptions().update(options)

    def add_yoptions(self, options):
        self._get_yoptions().update(options)

    def set_title(self, title):
        self.layout['title'] = title

    def set_xtitle(self, title):
        if title is not None:
            self.xoptions['title'] = title

    def set_ytitle(self, title):
        if title is not None:
            self.yoptions['title'] = title

    def set_ytitle2(self, title):
        if title is not None:
            self.yoptions2['title'] = title


    def set_xaxistype(self, axis_type):
        if axis_type is not None and axis_type != 'auto':
            self.xoptions['type'] = axis_type
            self.xoptions['nticks'] = 10

    def set_xreversed(self, reverse):
        if reverse:
            self.xoptions['autorange'] = 'reversed'

    def set_yreversed(self, reverse):
        if reverse:
            self.yoptions['autorange'] = 'reversed'

    def set_auto_margining(self, auto_margin):
        if auto_margin:
            self.yoptions['automargin'] = True
            self.xoptions['automargin'] = True

    def set_xaxis(self):
        self.layout['xaxis'] = self.xoptions

    def set_yaxis(self):
        self.layout['yaxis'] = self.yoptions

    def set_yaxis2(self):
        self.yoptions2['side'] = 'right'
        self.yoptions2['overlaying'] = 'y'
        self.layout['yaxis2'] = self.yoptions2

    def set_legend_options(self, legend_options):
        if legend_options is None:
            legend_options = dict(orientation='h')
        self.layout['legend'] = legend_options

    def set_bgcolour(self, colour):
        self.layout.update({'paper_bgcolor' : colour, 'plot_bgcolor' : colour})
        super(Chart, self).set_bgcolour(colour)

    def _apply_colours(self, colours):
        if colours is None:
            self.layout['colorway'] = utils.get_colour_set('Default')
        else:
            if isinstance(colours, list):
                self.layout['colorway'] = colours
            else:
                colours = utils.get_colour_set(colours)
                if colours is None:
                    raise ValueError('Specify a list of colours or one of: '+
                                     str(list(utils.COLOURS)))
                self.layout['colorway'] = colours
        return colours

    def toDiv(self):
        return tmp.CHART_TEMPLATE.render(chart=self)

    def _plot(self, output_type):
        figure = graphs.Figure(data=self.get_plot_data(), layout=self._get_layout())
        include_js = output_type == 'file'
        return py.offline.plot(figure_or_data=figure, show_link=False,
                               output_type=output_type, include_plotlyjs=include_js,
                               config={'displayModeBar':False})


    def _get_xaxis(self, col):
        if self._is_horizontal():
            return self._get_values(col)
        return self._get_filtered_row_headers()

    def _get_yaxis(self, col):
        if self._is_horizontal():
            return self._get_filtered_row_headers()
        return self._get_values(col)

    def _is_horizontal(self):
        return self.options.get('orientation') == 'h'

    def _get_options(self):
        chart_options = self.options
        self.set_title(chart_options.pop('title', None))
        self.set_xtitle(chart_options.pop('xlabel', None))
        self.set_ytitle(chart_options.pop('ylabel', None))
        self.set_ytitle2(chart_options.pop('ylabel2', None))
        self.set_xaxistype(chart_options.pop('xtype', None))
        self.set_xreversed(chart_options.pop('xreverse', False))
        self.set_yreversed(chart_options.pop('yreverse', False))
        self.set_auto_margining(chart_options.pop('autoMargin', False))
        self.set_colours(chart_options.pop('colours', None))
        self.set_xaxis()
        self.set_yaxis()
        self.set_yaxis2()
        self.set_legend_options(chart_options.pop('legend', None))
        bgcolour = chart_options.pop('bgcolour', None)
        if bgcolour is not None:
            self.set_bgcolour(bgcolour)
        return chart_options

    @abstractmethod
    def get_plot_data(self):
        pass

class PieChart(Chart):

    def get_plot_data(self):
        data = []
        options = self._get_options()
        for col_header in self._get_filtered_col_headers():
            data.append(graphs.Pie(labels=self._get_xaxis(col_header),
                                   values=self._get_yaxis(col_header), name=col_header, **options))
        return data

class DonutChart(PieChart):

    def _get_options(self):
        options = super(DonutChart, self)._get_options()
        options['hole'] = options.pop('hole', .5)
        return options

    def _get_layout(self):
        layout = super(DonutChart, self)._get_layout()
        layout['annotations'] = [dict(text=layout.pop('title', None),
                                      showarrow=False, font={'size':15})]
        return layout

class BarChart(Chart):

    def _get_options(self):
        bar_options = super(BarChart, self)._get_options()
        colour = self._get_rgbcolour(bar_options.pop('colour', None))
        line_colour = self._get_rgbcolour(bar_options.pop('lineColour', colour))
        line_width = bar_options.pop('lineWidth', '1')
        if colour is not None:
            bar_options['marker'] = dict(color=colour, line=dict(color=line_colour, width=line_width))
        return bar_options

    def get_plot_data(self):
        data = []
        options = self._get_options()
        for col_header in self._get_filtered_col_headers():
            opts = graphs.Bar(x=self._get_xaxis(col_header),
                              y=self._get_yaxis(col_header), name=col_header, **options)
            data.append(opts)
        return data

class StackedBarChart(BarChart):

    def _get_layout(self):
        bar_layout = super(StackedBarChart, self)._get_layout()
        bar_layout['barmode'] = 'stack'
        return bar_layout

class RelativeBarChart(BarChart):

    def _get_layout(self):
        bar_layout = super(RelativeBarChart, self)._get_layout()
        bar_layout['barmode'] = 'relative'
        return bar_layout

class LineChart(Chart):

    def _get_options(self):
        line_options = super(LineChart, self)._get_options()
        line_colour = self._get_rgbcolour(line_options.pop('lineColour', None))
        line_width = line_options.pop('lineWidth', '1')
        interpolate = line_options.pop('interpolate', 'linear')
        line = line_options.pop('line', 'solid')
        if ((line != 'solid') or (line_colour is not None) or
                (line_width != '1') or (interpolate != 'linear')):
            line_options['line'] = dict(color=line_colour, width=line_width,
                                        dash=line, shape=interpolate)
        return line_options

    def get_plot_data(self):
        data = []
        options = self._get_options()
        for col_header in self._get_filtered_col_headers():
            data.append(graphs.Scatter(x=self._get_xaxis(col_header),
                                       y=self._get_yaxis(col_header), name=col_header, **options))
        return data

class AreaChart(LineChart):

    def _get_options(self):
        line_options = super(AreaChart, self)._get_options()
        line_options['fill'] = 'tonexty'
        colour = self._get_rgbcolour(line_options.pop('colour', None))
        if colour is not None:
            line_options['fillcolor'] = colour
        return line_options

class Histogram(Chart):

    def __init__(self, response, **options):
        self._range_start = None
        self._range_end = None
        super(Histogram, self).__init__(response, **options)

    def _get_options(self):
        hist_options = super(Histogram, self)._get_options()
        bin_size = hist_options.pop('binSize', None)
        bin_number = hist_options.pop('binNumber', None)

        if bin_size is not None and bin_number is not None:
            raise ValueError("Cannot specify both bin_size and bin_number for Histogram")

        if bin_number is not None:
            bin_size = self._get_calculated_bin_size(bin_number)

        if bin_size is not None:
            hist_options['xbins'] = dict(size=bin_size,
                                         start=self._range_start, end=self._range_end)
        return hist_options

    def _get_xaxis(self, col):
        x_axis = self._get_values(col)
        self._calculate_range(x_axis)
        return x_axis

    def _get_calculated_bin_size(self, bin_number):
        full_range = self._range_end - self._range_start
        return full_range/bin_number

    def _calculate_range(self, array):
        try:
            val_range = np.array(array).astype(np.float)
            self._range_start = min(val_range)
            self._range_end = max(val_range)
        except ValueError:
            pass
            #self._rangeStart = None
            #self._rangeEnd = None

    def get_plot_data(self):
        data = []
        for col_header in self._get_filtered_col_headers():
            data.append(graphs.Histogram(x=self._get_xaxis(col_header),
                                         name=col_header, **self._get_options()))
        return data

class DistChart(Chart):
    def __init__(self, response, **options):
        self._bin_size = options.pop('binSize', 1.)
        super(DistChart, self).__init__(response, **options)

    def _get_options(self):
        hist_options = super(DistChart, self)._get_options()
        return hist_options

    def _get_xaxis(self, col):
        x_axis = np.array(self._get_values(col)).astype(np.float)
        return x_axis

    def get_plot_data(self):
        data = []
        group_labels = []
        for col_header in self._get_filtered_col_headers():
            data.append(self._get_xaxis(col_header))
            group_labels.append(col_header)

        return ff.create_distplot(data, group_labels, bin_size=self._bin_size)

    def _plot(self, output_type):
        data = self.get_plot_data()
        data['layout'].update(self._get_layout())
        include_js = output_type == 'file'
        return py.offline.plot(data, show_link=False, output_type=output_type,
                               include_plotlyjs=include_js, config={'displayModeBar':False})

class HeatMapChart(Chart):

    def set_colours(self, colours):
        #needs a colourscale like [[0, '#FFFFFF'], [1, '#9C27B0']]
        #or name of predefined plotly scale
        if colours is not None:
            colour_scale = colours
            if isinstance(colours, list):
                colour_scale = utils.get_calculated_colour_scale(colours)
            elif utils.get_colour_set(colours) is not None:
                #custom predefined colours have a 'base' colour at the start so just use that as the end colour
                end_colour = utils.get_colour_set(colours)[0]
                colour_scale = utils.get_calculated_colour_scale([end_colour])
            # else  -could be predefined plotly colour scale
            self.options.update({'colorscale': colour_scale})

    def get_plot_data(self):
        data = []
        heat_array = []
        for row_header in self._get_filtered_row_headers():
            values = []
            for col_header in self._get_filtered_col_headers():
                values.append(self._get_value(row_header, col_header))
            heat_array.append(values)

        x_axis = self._get_filtered_col_headers()
        y_axis = self._get_filtered_row_headers()

        #self.xoptions['showticklabels'] = False
        #self.yoptions['showticklabels'] = False
        self.set_yreversed(True)

        data.append(graphs.Heatmap(x=x_axis, y=y_axis, z=heat_array, **self._get_options()))
        return data

class WorldMap(Chart):
    def __init__(self, response, **options):
        super(WorldMap, self).__init__(response, **options)
        self.layout['geo'] = dict(bgcolor='rgba(0,0,0,0)', showframe=False,
                                  projection=dict(type=self.options.pop('projection', 'equirectangular')))
        self.layout['margin'] = dict(l=0, r=0, t=0, b=0)

    def get_plot_data(self):
        data = []
        for col_header in self.response.get_col_headers():
            if (self.col_filter is None or col_header in self.col_filter):
                data.append(graphs.Choropleth(locations=self._get_xaxis(col_header),
                                              z=self._get_yaxis(col_header), **self._get_options()))
        return data

    def set_font(self, style):
        super(WorldMap, self).set_font(style)
        self.layout.update({'geo' : dict(bgcolor='rgba(0,0,0,0)',
                                         coastlinecolor=style.font_colour, showframe=False,
                                         projection=dict(type=self.options.pop('projection', 'equirectangular')))})

    def _get_options(self):
        options = super(WorldMap, self)._get_options()
        options['locationmode'] = 'country names'
        return options

    def set_colours(self, colours):
        #needs a colourscale like [[0, '#FFFFFF'], [1, '#9C27B0']] or name of predefined plotly scale
        if colours is not None:
            colour_scale = colours
            if isinstance(colours, list):
                colour_scale = utils.get_calculated_colour_scale(colours)
            elif utils.get_colour_set(colours) is not None:
                #custom predefined colours have a 'base' colour at the start so just use that as the end colour
                end_colour = utils.get_colour_set(colours)[0]
                colour_scale = utils.get_calculated_colour_scale([end_colour])
            # else  -could be predefined plotly colour scale
            self.options.update({'colorscale': colour_scale})

class ComboChart(Chart):
    def __init__(self, *charts, **options):
        super(ComboChart, self).__init__(None, **options)
        self._charts = charts

    def get_plot_data(self):
        self._get_options()
        data = []
        for chart in self._charts:
            for plot_data in chart.get_plot_data():
                data.append(plot_data)
        return data
