from datetime import datetime, timedelta
from io import StringIO

import requests
import pandas as pd

from . import __fund_base as fund_base


class Morningstar(fund_base.FundBase):

    def __init__(self, id, name=None):
        super().__init__(id, name)

    def csv_url(self):
        return "http://www.morningstar.co.jp/FundData/DownloadStdYmd.do?fnc=" + self.id

    def detail_url(self):
        return "http://www.morningstar.co.jp/FundData/SnapShot.do?fnc=" + self.id

    def get(self):
        url = self.csv_url()
        tomorrow = datetime.now() + timedelta(days=1)
        data = {"selectStdYearFrom": "1990",
                "selectStdMonthFrom": "1",
                "selectStdDayFrom": "1",
                "selectStdYearTo": str(tomorrow.year),
                "selectStdMonthTo": str(tomorrow.month),
                "selectStdDayTo": str(tomorrow.day),
                "base": "0"}
        response = requests.post(url, data=data)
        if response.status_code / 100 == 2:
            response.encoding = "sjis"
            def my_parser(date): return pd.datetime.strptime(date, "%Y%m%d")
            return pd.read_csv(StringIO(response.text),
                               names=('Date', 'Price'),
                               header=0,
                               date_parser=my_parser,
                               index_col=0)
        else:
            raise "error"
