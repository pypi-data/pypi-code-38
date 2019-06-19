import unittest
import httpretty
from models.exchangerate import ExchangeService

class test_function(unittest.TestCase):

    @httpretty.activate()
    def test_request_latest(self):
        body_from_latest = '{"abc"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest", body = body_from_latest)
        Response_from_main = ExchangeService().get_latest()
        self.assertEqual(Response_from_main,body_from_latest)
        httpretty.disable()

    @httpretty.activate
    def test_request_time(self):
        httpretty.activate()
        body_from_time = '{"base":"EUR","rates":{"BGN":1.9558},"date":"2007-12-20"}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/2007-12-20", body = body_from_time)
        Response_from_main = ExchangeService().get_by_time('20', '12', '2007')
        self.assertEqual(Response_from_main,body_from_time)

    @httpretty.activate
    def test_reqest_base(self):
        body_from_base = '{"base":"EUR", "rates":{"BGN":1.6989}}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest?base=USD", body = body_from_base)
        Response_from_main = ExchangeService().get_by_base('USD')
        self.assertEqual(Response_from_main,body_from_base)


    @httpretty.activate
    def test_reqest_symbols(self):
        body_from_symbols = '{"base":"EUR", "rates":{"BGN":1.6989}, "symbols" : {"ILS","JPY"}}'
        httpretty.register_uri(httpretty.GET, "https://api.exchangeratesapi.io/latest?symbols=USD,GBP", body = body_from_symbols)
        Response_from_main = ExchangeService().get_by_symbols("USD,GBP")
        self.assertEqual(Response_from_main,body_from_symbols)


if __name__ == '__main__':
    unittest.main()
