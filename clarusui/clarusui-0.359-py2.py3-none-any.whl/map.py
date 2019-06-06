from __future__ import division
import plotly.graph_objs as graphs
from clarusui.chart import Chart
from clarusui import utils


class WorldMap(Chart):
    def __init__(self, response, **options):
        super(WorldMap, self).__init__(response, **options)
        self.layout['geo'] = dict(bgcolor='rgba(0,0,0,0)', showframe=False,
                                  projection=dict(type=self.options.pop('projection', 'equirectangular')))
        self.layout['margin'] = dict(l=0, r=0, t=0, b=0)

    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers():
            if (self.colFilter == None or colHeader in self.colFilter):
                data.append(graphs.Choropleth(locations=self._get_xaxis(colHeader), z=self._get_yaxis(colHeader),
                                              **self._get_options()))
        return data
    
    def set_font(self, style):
        super(WorldMap, self).set_font(style)
        self.layout.update({'geo' : dict(bgcolor='rgba(0,0,0,0)', coastlinecolor=style.fontColour, showframe=False,
                                  projection=dict(type=self.options.pop('projection', 'equirectangular')))})
        
    
    def _get_options(self):
        options = super(WorldMap, self)._get_options()
        options['locationmode'] = 'country names'
        return options
    
    def set_colours(self, colours):
        #needs a colourscale like [[0, '#FFFFFF'], [1, '#9C27B0']] or name of predefined plotly scale
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
        
        
            
        
