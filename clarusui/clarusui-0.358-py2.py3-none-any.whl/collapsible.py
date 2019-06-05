from clarusui.layout import Element
from clarusui.table import Table
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pandas import DataFrame
from datetime import datetime, timedelta

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
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, response, scrollSpeed=5, **options):
        super(EventTicker, self).__init__(scrollSpeed=scrollSpeed, body=Table(response), scroll=True, **options)
        self.set_header(self._extract_latest(response))
        
    def _add_meta(self, result):
        resultMeta = {}
        resultMeta['latestTime'] = self._latestTime
        result['resultMeta'] = resultMeta
        return result
    
    def _set_event(self, event):
        super(EventTicker, self)._set_event(event)
        self._process_meta()
            
    def _process_meta(self):
        meta = self._get_meta()
        if meta is not None:
            latestTime = meta.get('latestTime')
            if latestTime == self._latestTime:
                self._scrollHeader = False
        elif meta is None or ((latestTime is None or latestTime == '') and self._latestTime != ''):
                latestTimeStamp = datetime.strptime(self._latestTime, self.DATE_TIME_FORMAT)
                nowMinusTwoMins = datetime.utcnow() - timedelta(minutes=2)
                print(latestTimeStamp)
                print(nowMinusTwoMins)
                if latestTimeStamp < nowMinusTwoMins:
                    self._scrollHeader = False;
                

    def _extract_latest(self, response):
        results = response.results
        df = DataFrame(results)
        self._latestTime = '' 
        if df.empty:
            return ''
        
        else:
            last = df.tail(1)
            lastTime = last.iloc[0]['Time']
            latestRows = df.loc[df['Time'] == lastTime]
            
            extracted = []
            
            for index, row in latestRows.iterrows():
                extracted.append('<i class="fa fa-clock-o"></i>  ' + row['Time'] + ' ' + row['Description'])
                
            currentDate = datetime.utcnow().date()
            latestTimeStamp = datetime.combine(currentDate, datetime.strptime(lastTime, '%H:%M:%S').time())
            self._latestTime = latestTimeStamp.strftime(self.DATE_TIME_FORMAT)
                
            return ' '.join(extracted)
            
        #df = df.set_index(df.columns[0])
        #print(df.tail(1))
        
        
