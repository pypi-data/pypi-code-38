"""Object with header and collapsible body."""
from datetime import datetime, timedelta
from pandas import DataFrame
from clarusui.layout import Element
from clarusui.table import Table
from clarusui import templates as tmp

class Collapsible(Element):
    def __init__(self, **options):
        self._body = options.pop('body', '')
        self.scroll_header = options.pop('scroll', False)
        self._scroll_speed = options.pop('scrollSpeed', 5)
        super(Collapsible, self).__init__(None, **options)

    def _get_scroll_period(self):
        if self.header is None or not self.header:
            return '0s'

        calced = 50/self._scroll_speed
        min_value = 1
        return str(max(calced, min_value)) + 's'

    def _get_body(self):
        if isinstance(self._body, Element):
            return self._body.toDiv()
        return self._body

    def set_style(self, style):
        super(Collapsible, self).set_style(style)
        if isinstance(self._body, Element):
            self._body.set_style(style)

    def toDiv(self):
        return tmp.COLLAPSIBLE_TEMPLATE.render(card=self)

class EventTicker(Collapsible):
    DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, response, scrollSpeed=5, **options):
        super(EventTicker, self).__init__(scrollSpeed=scrollSpeed,
                                          body=Table(response), scroll=True, **options)
        self.set_header(self._extract_latest(response))

    def create_meta(self):
        return {'latestTime' : self._latest_time}
        #result_meta['latestTime'] = self._latest_time
        #result['resultMeta'] = result_meta
        #return result

    def process_meta(self):
        meta = self.get_meta()
        if meta is not None:
            meta_latest_time = meta.get('latestTime')
            if meta_latest_time == self._latest_time:
                self.scroll_header = False #timestamp already ticked across
        elif self._latest_time is None or self._latest_time == '':
            self.scroll_header = False #empty event table
        elif meta is None or meta_latest_time is None or meta_latest_time == '': #no meta
            latest_time_stamp = datetime.strptime(self._latest_time, self.DATE_TIME_FORMAT)
            now_minus_two_mins = datetime.utcnow() - timedelta(minutes=2)
            if latest_time_stamp < now_minus_two_mins:
                self.scroll_header = False #don't tick if latest event older that 2 mins


    def _extract_latest(self, response):
        results = response.results
        data_frame = DataFrame(results)
        self._latest_time = '' #using string, needs to be json serialised
        if data_frame.empty:
            return ''

        last = data_frame.tail(1)
        last_time = last.iloc[0]['Time']
        latest_rows = data_frame.loc[data_frame['Time'] == last_time]

        extracted = []

        for index, row in latest_rows.iterrows():
            extracted.append('<i class="fa fa-clock-o"></i>  ' +
                             row['Time'] + ' ' + row['Description'])

        current_date = datetime.utcnow().date()
        latest_time_stamp = datetime.combine(current_date,
                                             datetime.strptime(last_time, '%H:%M:%S').time())
        self._latest_time = latest_time_stamp.strftime(self.DATE_TIME_FORMAT)

        return ' '.join(extracted)
