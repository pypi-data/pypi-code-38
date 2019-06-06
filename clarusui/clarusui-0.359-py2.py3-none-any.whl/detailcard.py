import clarusui as ui
from clarusui.layout import Element
from jinja2 import Environment, FileSystemLoader, select_autoescape
import clarusui.colours
import os
from collections import OrderedDict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml']))

cardTemplate = env.get_template('detailcard.html')


class DetailCard(Element):
    def __init__(self, response=None, **options):
        super(DetailCard, self).__init__(response, **options)
        self._icon = options.pop('icon', None)
        self._iconColour = options.pop('iconColour', None) 
        self._body = options.pop('body', '')
        self._detailsMap = options.pop('detailsMap', None) 
        #self.add_custom_css({'height':'100%'})
        self.add_custom_css({'height':'100%', 'min-width':'200px'})
        
    def set_last_move(self, lastMove):
        super(DetailCard, self).set_last_move(lastMove)
        self.moveIcon = self._get_last_move_icon()

    def _get_last_move_icon(self):
        if self.lastMove is None or self.lastMove == 0:
            return None
        if self.lastMove > 0:
            return 'fa fa-caret-up'
        else:
            return 'fa fa-caret-down'
        
    def _get_formatted_string(self, value):
        try:
            value = float(str(value).replace(',', ''))
        except:
            return value
        
        absValue = abs(value)
        if absValue >= 1000000000:
            scaledVal = value/1000000000
            format = '{:,.1f}'
            unit = 'b'
        elif absValue >= 1000000:
            scaledVal = value/1000000
            if absValue > 10000000:
                format = '{:,.0f}'
            else:
                format = '{:,.1f}'
            unit = 'm'
        elif absValue >= 1000:
            scaledVal = value/1000
            if absValue > 10000:
                format = '{:,.0f}'
            else:
                format = '{:,.1f}'
            unit = 'k'
        else:
            scaledVal = value
            format = '{:,.0f}'
            unit = ''
        return format.format(scaledVal) + unit
        
        
    @property
    def icon(self):
        return self._icon
    
    @property
    def iconColour(self):
        return self._iconColour
    
    @property
    def body(self):
        return self._get_formatted_string(self._body)
    
    @property
    def detailsMap(self):
        if self._detailsMap is None:
             return None
        
        for k, v in self._detailsMap.items():
            self._detailsMap[k] = self._get_formatted_string(v)
        return self._detailsMap
    
    @property
    def hasDetails(self):
        return self.detailsMap is not None and len(self.detailsMap) > 0
    
    @property
    def rowSpan(self):
        if self._detailsMap is None:
            return 1
        else:
            return len(self._detailsMap)

    def toDiv(self):
        return cardTemplate.render(card=self)
    
class RTDetailCard(DetailCard):
    def __init__(self, response, **options):
        super(RTDetailCard, self).__init__(response, **options)
        self.set_header(self.response.get_result_title())
        self._body = self.response.total
        if self.lastMoveResponse is not None and 'Total' in self.lastMoveResponse.get_col_headers() and 'Total' in self.lastMoveResponse.get_row_headers():
            self.set_last_move(self.lastMoveResponse.get_float_value('Total', 'Total'))
        self._set_details()
    
    def _set_details(self):
        detailMap = OrderedDict()
        if self.otherResponses is not None:
            for resp in self.otherResponses:
                if 'Total' in resp.get_col_headers() and 'Total' in resp.get_row_headers():
                    detailMap[resp.context] = resp.get_float_value('Total', 'Total')
        self._detailsMap = detailMap
            
            
        
                
            
    