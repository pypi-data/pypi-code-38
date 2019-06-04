import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
import plotly.graph_objs as graphs
import plotly.offline as py
import plotly.figure_factory as ff
from clarusui.gridvisualisationelement import GridViz
from abc import ABCMeta, abstractmethod
import numpy as np
from clarusui import utils

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    #loader=FileSystemLoader('/templates/'),
    autoescape=select_autoescape(['html', 'xml'])
)

chart_template = env.get_template('chart.html')

class Chart(GridViz):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        self.layout     = dict()
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
            font['color'] = style.fontColour
            font['family'] = style.fontFamily
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

    
    def set_xaxistype(self, type):
        if type is not None and type != 'auto':
            self.xoptions['type'] = type
            self.xoptions['nticks'] = 10
        
    def set_xreversed(self, reverse):
        if reverse == True:
            self.xoptions['autorange'] = 'reversed'

    def set_yreversed(self, reverse):
        if reverse == True:
            self.yoptions['autorange'] = 'reversed'
            
    def set_auto_margining(self, autoMargin):
        if autoMargin == True:
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
    
    def set_legend_options(self, legendOptions):
        if legendOptions is None:
            legendOptions = dict(orientation='h')
        self.layout['legend'] = legendOptions

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
                    raise ValueError('Specify a list of colours or one of: '+ str(list(utils.COLOURS)))
                self.layout['colorway'] = colours
        return colours
        

    def toDiv(self):
        return chart_template.render(chart=self)

    def _plot(self, output_type):
        figure = graphs.Figure(data=self._get_plot_data(), layout=self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(figure_or_data=figure, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
        
    
    def _get_xaxis(self, col):
        if self.isHorizontal():
            return self._get_values(col)
        else:
            return self._get_filtered_row_headers()

    def _get_yaxis(self, col):
        if self.isHorizontal():            
            return self._get_filtered_row_headers() 
        else:
            return self._get_values(col)

    def isHorizontal(self):
        return self.options.get('orientation')=='h'
    
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
        if (bgcolour is not None):
            self.set_bgcolour(bgcolour)
        return chart_options
               
    @abstractmethod        
    def _get_plot_data(self):
        pass

class PieChart(Chart):

    def __init__(self, response, **options):
        super(PieChart, self).__init__(response, **options)
        
    def _get_plot_data(self):
        data = []
        options = self._get_options()
        for colHeader in self._get_filtered_col_headers():
            data.append(graphs.Pie(labels=self._get_xaxis(colHeader), values=self._get_yaxis(colHeader), name=colHeader, **options))                    
        return data
        
class DonutChart(PieChart):
        
    def __init__(self, response, **options):
        super(DonutChart, self).__init__(response, **options)
        
    def _get_options(self):
        options = super(PieChart, self)._get_options()     
        options['hole'] = options.pop('hole', .5)
        return options
            
    def _get_layout(self):
        layout =  super(DonutChart, self)._get_layout()        
        layout['annotations'] = [dict(text=layout.pop('title', None), showarrow=False, font={'size':15})]
        return layout
   
class BarChart(Chart):

    def __init__(self, response, **options):
        super(BarChart, self).__init__(response, **options)
        
    def _get_options(self):
        bar_options =  super(BarChart, self)._get_options()
        colour = self._get_rgbcolour(bar_options.pop('colour', None))
        lineColour = self._get_rgbcolour(bar_options.pop('lineColour', colour))
        lineWidth = bar_options.pop('lineWidth', '1')
        if (colour is not None):
            bar_options['marker'] = dict(color=colour, line=dict(color=lineColour, width=lineWidth))
        return bar_options
        
    def _get_plot_data(self):
        data = []
        options = self._get_options()
        for colHeader in self._get_filtered_col_headers():
            opts = graphs.Bar(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **options)
            data.append(opts)             
        return data
        
class StackedBarChart(BarChart):

    def __init__(self, response, **options):
        super(StackedBarChart, self).__init__(response, **options)
        
    def _get_layout(self):
        bar_layout =  super(StackedBarChart, self)._get_layout()
        bar_layout['barmode'] = 'stack'
        return bar_layout
    
class RelativeBarChart(BarChart):

    def __init__(self, response, **options):
        super(RelativeBarChart, self).__init__(response, **options)
        
    def _get_layout(self):
        bar_layout =  super(RelativeBarChart, self)._get_layout()
        bar_layout['barmode'] = 'relative'
        return bar_layout
    
class LineChart(Chart):

    def __init__(self, response, **options):
        super(LineChart, self).__init__(response, **options)

    def _get_options(self):
        line_options = super(LineChart, self)._get_options()
        lineColour = self._get_rgbcolour(line_options.pop('lineColour', None))
        lineWidth = line_options.pop('lineWidth', '1')
        interpolate = line_options.pop('interpolate', 'linear')
        line = line_options.pop('line', 'solid')
        if (line!='solid') or (lineColour is not None) or (lineWidth!='1') or (interpolate!='linear'):
            line_options['line'] = dict(color=lineColour, width=lineWidth, dash=line, shape=interpolate);
        return line_options        

    def _get_plot_data(self):
        data = []
        options = self._get_options()
        for colHeader in self._get_filtered_col_headers():
            data.append(graphs.Scatter(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **options))                 
        return data
    
class AreaChart(LineChart):

    def __init__(self, response, **options):
        super(AreaChart, self).__init__(response, **options)
    
    def _get_options(self):
        line_options =  super(AreaChart, self)._get_options()
        line_options['fill'] = 'tonexty'
        colour = self._get_rgbcolour(line_options.pop('colour', None))
        if colour is not None:
            line_options['fillcolor'] = colour
        return line_options

class Histogram(Chart):
    
    def __init__(self, response, **options):
        super(Histogram, self).__init__(response, **options)
        
    def _get_options(self):
        hist_options =  super(Histogram, self)._get_options()
        binSize = hist_options.pop('binSize', None)
        binNumber = hist_options.pop('binNumber', None)
        
        if binSize is not None and binNumber is not None:
            raise ValueError("Cannot specify both binSize and binNumber for Histogram")
        
        if binNumber is not None:
            binSize = self._get_calculated_bin_size(binNumber)
        
        if binSize is not None:
            hist_options['xbins'] = dict(size=binSize, start=self._rangeStart, end=self._rangeEnd)
        return hist_options
        
    def _get_xaxis(self, col):
        x = self._get_values(col)
        self._calculate_range(x)
        return x
    
    def _get_calculated_bin_size(self, binNumber):
        range = self._rangeEnd - self._rangeStart
        return range/binNumber
    
    def _calculate_range(self, array):
        try:
            x = np.array(array).astype(np.float)
            self._rangeStart = min(x)
            self._rangeEnd = max(x)
        except ValueError:
            self._rangeStart = None
            self._rangeEnd = None
           
    def _get_plot_data(self):
        data = []
        for colHeader in self._get_filtered_col_headers():
            data.append(graphs.Histogram(x=self._get_xaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
    
class DistChart(Chart):
    def __init__(self, response, **options):
        self._binSize = options.pop('binSize', 1.)
        super(DistChart, self).__init__(response, **options)
        
    def _get_options(self):
        hist_options =  super(DistChart, self)._get_options()
        return hist_options

    def _get_xaxis(self, col):
        x = np.array(self._get_values(col)).astype(np.float)
        return x
    
    def _get_plot_data(self):
        data = []
        groupLabels = []
        for colHeader in self._get_filtered_col_headers():
            data.append(self._get_xaxis(colHeader))
            groupLabels.append(colHeader)
                
        return ff.create_distplot(data, groupLabels, bin_size=self._binSize)                 

    
    def _plot(self, output_type):
        data=self._get_plot_data()
        data['layout'].update(self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(data, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
    
class HeatMapChart(Chart):
    def __init__(self, response, **options):
        super(HeatMapChart, self).__init__(response, **options)
        
    def set_colours(self, colours):
        #needs a colourscale like [[0, '#FFFFFF'], [1, '#9C27B0']] or name of predefined plotly scale
        colourScale = self._get_calculated_colour_scale(['#0D47A1', '#E3F2FD', '#E8F5E9', '#1B5E20'])
        self.options.update({'colorscale': colourScale})
        return
        if colours is not None:
            colourScale = colours
            if isinstance(colours, list):
                colourScale = self._get_calculated_colour_scale(colours)
            elif utils.get_colour_set(colours) is not None:
                #custom predefined colours have a 'base' colour at the start so just use that as the end colour
                endColour = utils.get_colour_set(colours)[0]
                colourScale = self._get_calculated_colour_scale([endColour])
            # else  -could be predefined plotly colour scale
            self.options.update({'colorscale': colourScale})
            
    def _get_calculated_colour_scale(self, colourList):
        colourScale = []
        listSize = len(colourList)
        if listSize == 1 : #single colour, start from white
            colourList.insert(0, '#FFFFFF')
        
        stepSize = 1/(len(colourList) - 1)
        step = 0
        for colour in colourList:
            colourScale.append([step * stepSize, colour])
            step += 1
        
        return colourScale
        
    def _get_plot_data(self):
        data = []
        heatArray = []
        for rowHeader in self._get_filtered_row_headers():
            c = []
            for colHeader in self._get_filtered_col_headers():
                c.append(self._get_value(rowHeader, colHeader))
            heatArray.append(c)
            
        x = self._get_filtered_col_headers()
        y = self._get_filtered_row_headers()
        
        #self.xoptions['showticklabels'] = False
        #self.yoptions['showticklabels'] = False
        self.set_yreversed(True)
        
        data.append(graphs.Heatmap(x=x, y=y, z=heatArray, **self._get_options()))
        return data
        
    

class ComboChart(Chart):
    def __init__(self, *charts, **options):
        super(ComboChart, self).__init__(None, **options)
        self._charts = charts
        
    def _get_plot_data(self):
        self._get_options()
        data = []
        for chart in self._charts:
            for d in chart._get_plot_data():
                data.append(d)
        return data
    