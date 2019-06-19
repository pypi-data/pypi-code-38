import unittest
import httpretty
from services.exchangerate import ExchangeService

class test_function(unittest.TestCase):

    @httpretty.activate()
    def test_request_latest(self):
        body_from_latest = '{"base":"EUR","rates":{"BGN":1.9557},"date":"2019-06-18"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest", body = body_from_latest)
        Response_from_main = ExchangeService().get_latest()
        self.assertEqual(str(Response_from_main),"EUR - {'BGN': 1.9557} - 2019-06-18 - None - None")

    @httpretty.activate
    def test_request_time(self):
        httpretty.activate()
        body_from_time = '{"base":"EUR","rates":{"BGN":1.9558},"date":"2007-12-20"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/2007-12-20", body = body_from_time)
        Response_from_main = ExchangeService().get_by_time('20', '12', '2007')
        self.assertEqual(str(Response_from_main),"EUR - {'BGN': 1.9558} - 2007-12-20 - None - None")

    @httpretty.activate
    def test_request_base(self):
        body_from_base = '{"base":"USD", "rates":{"BGN":1.6989}}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest?base=USD", body = body_from_base)
        Response_from_main = ExchangeService().get_by_base('USD')
        self.assertEqual(str(Response_from_main),"USD - {'BGN': 1.6989} - None - None - None")

    @httpretty.activate
    def test_request_symbols(self):
        body_from_symbols = '{"base":"EUR","rates":{"USD":1.1187,"GBP":0.89403},"date":"2019-06-18"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest?symbols=USD,GBP", body = body_from_symbols)
        Response_from_main = ExchangeService().get_by_symbols("USD,GBP")
        self.assertEqual(str(Response_from_main),"EUR - {'USD': 1.1187, 'GBP': 0.89403} - 2019-06-18 - None - None")

    @httpretty.activate
    def test_request_history(self):
        body_from_symbols = '{"base":"EUR","rates":{"USD":1.1187,"GBP":0.89403},"start_at":"2018-01-01","end_at":"2018-09-01"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/history?start_at=2018-01-01&end_at=2018-09-01",
                               body=body_from_symbols)
        Response_from_main = ExchangeService().get_by_history(1,1,2018,1,9,2018)
        self.assertEqual(str(Response_from_main), "EUR - {'USD': 1.1187, 'GBP': 0.89403} - None - 2018-01-01 - 2018-09-01")


if __name__ == '__main__':
    unittest.main()

