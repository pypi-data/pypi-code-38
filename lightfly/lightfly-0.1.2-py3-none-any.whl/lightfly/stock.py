import pandas as pd
from pandas.compat import StringIO


class Stock(object):

    def __init__(self, http_client):
        self.http_client = http_client

    def hs300(self):
        path_info = '/api/stock/hs300'
        content = self.http_client.get(path_info)

        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def daily_history(self, symbol, date_from, date_to):
        path_info = '/api/stock/history/daily'
        content = self.http_client.get(path_info, {
            'date_from': date_from,
            'date_to': date_to,
            'symbol': symbol,
        })

        return pd.read_csv(StringIO(content), index_col=0, header=0, parse_dates=True)

    def stock_realtime(self, symbols):
        path_info = '/api/stock/realtime'
        content = self.http_client.get(path_info, {
            'symbols': symbols
        })
        return pd.read_csv(StringIO(content), index_col=0, header=0, parse_dates=True)

    def hgs_trade_realtime(self):
        path_info = '/api/stock/hgs/trade/realtime'
        content = self.http_client.get(path_info, {})

        return pd.read_csv(StringIO(content), header=0)

    def hgtong_top10(self):
        path_info = '/api/stock/hgtong/top10'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sgtong_top10(self):
        path_info = '/api/stock/sgtong/top10'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def ggtong_top10(self):
        path_info = '/api/stock/ggtong/top10'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def stock_index(self):
        path_info = '/api/stock/index'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sh_index_component(self):
        path_info = '/api/stock/component/shindex'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sh_consumption_index_component(self):
        path_info = '/api/stock/component/shconsumptionindex'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sh50_index_component(self):
        path_info = '/api/stock/component/sh50index'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sh_medicine_index_component(self):
        path_info = '/api/stock/component/shmedicineindex'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sz_index_component(self):
        path_info = '/api/stock/component/szindex'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def sz_composite_index_component(self):
        path_info = '/api/stock/component/szcompositeindex'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def zz500_index_component(self):
        path_info = '/api/stock/component/zz500index'
        content = self.http_client.get(path_info, {})
        return pd.read_csv(StringIO(content), index_col=0, header=0)

    def indicator_main(self, symbol):
        path_info = '/api/stock/indicator/main'
        content = self.http_client.get(path_info, {
            symbol: symbol
        })
        return pd.read_csv(StringIO(content), index_col=0, header=0)
