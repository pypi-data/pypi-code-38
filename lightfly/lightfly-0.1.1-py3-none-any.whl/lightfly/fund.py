import pandas as pd
from pandas.compat import StringIO


class Fund(object):

    def __init__(self, http_client):
        self.http_client = http_client

    def daily_history(self, symbol, date_from, date_to):
        path_info = '/api/fund/history/daily'
        content = self.http_client.get(path_info, {
            'symbol': symbol,
            'date_from': date_from,
            'date_to': date_to
        })

        return pd.read_csv(StringIO(content), index_col=0, header=0, parse_dates=True)
