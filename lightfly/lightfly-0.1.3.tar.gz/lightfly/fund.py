import pandas as pd
from pandas.compat import StringIO
import json


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

    def internet_banking(self):
        path_info = '/api/fund/internet/banking'
        content = self.http_client.get(path_info, {})

        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def basic_info(self, symbol):
        path_info = '/api/fund/basic/info'
        content = self.http_client.get(path_info, {
            'symbol': symbol
        })
        return json.loads(content)

    # 数据有问题，数值过大会包含额外的逗号
    # def stocks_holding(self, symbol):
    #     path_info = '/api/fund/stocks/holding'
    #     content = self.http_client.get(path_info, {
    #         'symbol': symbol
    #     })
    #
    #     print(content)
    #     exit(1)
    #
    #     return pd.read_csv(StringIO(content), header=0)
