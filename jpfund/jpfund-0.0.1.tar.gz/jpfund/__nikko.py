from datetime import datetime, timedelta
from io import StringIO

import requests
import pandas as pd
from pyquery import PyQuery as pq

from . import __fund_base as fund_base


class Nikko(fund_base.FundBase):

    def __init__(self, id, name=None):
        super().__init__(id, name)

    def csv_url(self):
        return "https://www.nikkoam.com/products/detail/%s/data/?format=xls" % self.id

    def detail_url(self):
        return "https://www.nikkoam.com/products/detail/%s" % self.id

    def get(self):
        url = self.csv_url()
        response = requests.get(url)
        if response.status_code / 100 == 2:
            response.encoding = "utf-8"
            # print(response.text)
            def my_parser(date): return pd.datetime.strptime(date, "%Y/%m/%d")
            return pd.read_csv(StringIO(response.text),
                               names=('Date', 'Price',
                                      'Change', 'Distribution', 'Total assets', 'Gross'),
                               header=1,
                               date_parser=my_parser,
                               index_col=0)
        else:
            raise "error"

    @classmethod
    def get_list(cls):
        html = pq(url="https://www.nikkoam.com/products/hotnews")
        contents = html(".com_hotnews")
        table = contents("#tableWithFloatingHeader")
        link_list = table(".fund_name")("a")
        link_name = [[pq(i).attr("href"), pq(i).text().replace("\n", " ")]
                     for i in link_list]
        id_name = [[i[0].split("/")[-2], i[1]] for i in link_name]
        return [Nikko(e[0], e[1]) for e in id_name]
