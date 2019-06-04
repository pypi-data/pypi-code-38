from clarusui.layout import Element
from clarusui.table import Table
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pandas import DataFrame

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml']))

collapsibleTemplate = env.get_template('collapsible.html')

class Collapsible(Element):
    def __init__(self, **options):
        self._body = options.pop('body', '')
        self._scrollHeader = options.pop('scroll', False)
        self._scrollSpeed = options.pop('scrollSpeed', 5)
        super(Collapsible, self).__init__(None, **options)
        
    def _get_scroll_period(self):
        if self._get_header() is None or len(self._get_header()) == 0:
            return '0s'
        else:
            calced = 50/self._scrollSpeed
            min = 1
            return str(max(calced, min)) + 's'
    
    def _get_body(self):
        if isinstance(self._body, Element):
            return self._body.toDiv()
        return self._body
    
    def _set_style(self, style):
        super(Collapsible, self)._set_style(style)
        if isinstance(self._body, Element):
            self._body._set_style(style)
        
    def toDiv(self):
        return collapsibleTemplate.render(card=self)
    
class EventTicker(Collapsible):
    def __init__(self, response, scrollSpeed=5, **options):
        super(EventTicker, self).__init__(scrollSpeed=scrollSpeed, body=Table(response), scroll=True, **options)
        self.set_header(self._extract_latest(response))
        
    def _extract_latest(self, response):
        results = response.results
        df = DataFrame(results)
        if df.empty:
            return ''
        
        else:
            last = df.tail(1)
            lastTime = last.iloc[0]['Time']
            latestRows = df.loc[df['Time'] == lastTime]
            
            extracted = []
            
            for index, row in latestRows.iterrows():
                extracted.append('<i class="fa fa-clock-o"></i>  ' + row['Time'] + ' ' + row['Description'])
                
            return ' '.join(extracted)
            
        #df = df.set_index(df.columns[0])
        #print(df.tail(1))
        
        
