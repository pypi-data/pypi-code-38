from datetime import datetime, timedelta
from io import StringIO

import requests
import pandas as pd
from pyquery import PyQuery as pq

from . import __fund_base as fund_base


class EMaxis(fund_base.FundBase):

    def __init__(self, id, name=None):
        super().__init__(id, name)

    def csv_url(self):
        return "https://emaxis.jp/content/csv/fundCsv.php?fund_cd=%s" % self.id

    def detail_url(self):
        return "https://emaxis.jp/fund/%s.html" % self.id

    def get(self):
        url = self.csv_url()
        response = requests.get(url)
        if response.status_code / 100 == 2:
            response.encoding = "sjis"
            # print(response.text)
            def my_parser(date): return pd.datetime.strptime(date, "%Y/%m/%d")
            return pd.read_csv(StringIO(response.text),
                               names=('Date', 'Price',
                                      'Gross', 'Distribution', 'Total assets'),
                               header=1,
                               date_parser=my_parser,
                               index_col=0)
        else:
            raise "error"

    @classmethod
    def get_list(cls):
        html = pq(url="https://emaxis.jp/fund/index.html")
        contents = html(".contentswrap")
        link_list = contents("a")
        id_name = [[pq(i).attr("href").replace(".html", ""), pq(i).text().replace("\n", " ")]
                   for i in link_list]
        return [EMaxis(e[0], e[1]) for e in id_name]
