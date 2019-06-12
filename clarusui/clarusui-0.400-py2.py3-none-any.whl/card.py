from collections import OrderedDict
from clarusui.layout import Element
from clarusui import templates as tmp

class Card(Element):
    def __init__(self, response=None, **options):
        super(Card, self).__init__(response, **options)
        self._icon = options.pop('icon', None)
        self._icon_colour = options.pop('iconColour', None) 
        self._body = options.pop('body', '')
        
    @property
    def icon(self):
        return self._icon
    
    @property
    def icon_colour(self):
        return self._icon_colour
    
    @property
    def body(self):
        return self._body

    def toDiv(self):
        return tmp.CARD_TEMPLATE.render(card=self)

class DetailCard(Card):
    def __init__(self, response=None, **options):
        super(DetailCard, self).__init__(response, **options)
        self._details_map = options.pop('detailsMap', None) 
        self.add_custom_css({'height':'100%', 'min-width':'200px'})
        
    def set_last_move(self, last_move=None, flash=True):
        super(DetailCard, self).set_last_move(last_move)
        self.move_icon = self._get_last_move_icon()

    def _get_last_move_icon(self):
        if self.last_move is None or self.last_move == 0:
            return None
        if self.last_move > 0:
            return 'fa fa-caret-up'
        return 'fa fa-caret-down'
        
    @staticmethod
    def _get_formatted_string(value):
        try:
            value = float(str(value).replace(',', ''))
        except:
            return value
        
        abs_value = abs(value)
        if abs_value >= 1000000000:
            scaled_val = value/1000000000
            number_format = '{:,.1f}'
            unit = 'b'
        elif abs_value >= 1000000:
            scaled_val = value/1000000
            if abs_value > 10000000:
                number_format = '{:,.0f}'
            else:
                number_format = '{:,.1f}'
            unit = 'm'
        elif abs_value >= 1000:
            scaled_val = value/1000
            if abs_value > 10000:
                number_format = '{:,.0f}'
            else:
                number_format = '{:,.1f}'
            unit = 'k'
        else:
            scaled_val = value
            number_format = '{:,.0f}'
            unit = ''
        return number_format.format(scaled_val) + unit

    @property
    def body(self):
        return self._get_formatted_string(self._body)
        
    @property
    def details_map(self):
        if self._details_map is None:
            return None
        
        for key, value in self._details_map.items():
            self._details_map[key] = self._get_formatted_string(value)
        return self._details_map
    
    @property
    def has_details(self):
        return self.details_map is not None and len(self.details_map) > 0
    
    @property
    def row_span(self):
        if self._details_map is None:
            return 1
        return len(self._details_map)

    def toDiv(self):
        return tmp.DETAIL_CARD_TEMPLATE.render(card=self)
    
class RTDetailCard(DetailCard):
    def __init__(self, response, **options):
        super(RTDetailCard, self).__init__(response, **options)
        self.set_header(self.response.get_result_title())
        self._body = self.response.total
        if (self.last_move_response is not None and
                'Total' in self.last_move_response.get_col_headers() and
                'Total' in self.last_move_response.get_row_headers()):
            self.set_last_move(self.last_move_response.get_float_value('Total', 'Total'))
        self._set_details()
    
    def _set_details(self):
        detail_map = OrderedDict()
        if self.other_responses is not None:
            for resp in self.other_responses:
                if 'Total' in resp.get_col_headers() and 'Total' in resp.get_row_headers():
                    detail_map[resp.context] = resp.get_float_value('Total', 'Total')
        self._details_map = detail_map
