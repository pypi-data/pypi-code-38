'''
import unittest
from pocket import Pocket
from datetime import datetime

pkt = Pocket(0)
pkt.order(datetime(2010, 9, 30), "A000030", 3)

sample_dict = {"A000660": 10, "A000400" : 100}
pkt.order(datetime(2011, 9, 30), sample_dict)

sample_dict = {"A000660": 1, "A000400": -10, "A000030" : 0}
pkt.order(datetime(2012, 9, 28), sample_dict)

class PocketTest(unittest.TestCase):
    def test(self):
        self.assertEqual(pkt.cur_stocks.at["A000660", "NAME"], "SK하이닉")

if __name__ == "__main__":
    unittest.main()
'''

# ---------- CHECK DATA PACKAGE ----------

from data import price

print(price.price_slow('삼성전자', start = '2019-01-01'))
print(price.price_slow(['삼성전자', 'SK하이닉스'], start = '2019-01-01'))

data = print(price.price_slow(['삼성전자', 'SK하이닉스'], start = '2019-01-01'))


