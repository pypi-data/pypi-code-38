from services.responses import ExchangeRateObject
from core.delegation.responsehandler import ResponseHandler
from core.resource import APIResource, Configuration

class ExchangeService(APIResource):
    def __init__(self):
        config = Configuration("https://api.exchangeratesapi.io", auth_handler=False, handler=ExchangeRateHandler, service_name='Exchange Rate Service(AMP)')
        super().__init__(config)


    def get_latest(self):
        querystring = '/latest'
        return self.get(querystring)


    def get_by_time(self , day , month , year):
        querystring = "/{}-{}-{}".format(year , month , day)
        return self.get(querystring)


    def get_by_base(self , moneyunit):
        querystring = "/latest?base={}".format(moneyunit)
        return self.get(querystring)


    def get_by_symbols(self , moneyunit):
        querystring =  "/latest?symbols={}".format(moneyunit)
        return self.get(querystring)


    def get_by_history(self , day1 , month1 , year1 , day2 , month2 , year2):
        querystring =  "/history?start_at={}-{}-{}&end_at={}-{}-{}".format(year1 , month1 , day1 ,year2 , month2 , day2)
        return self.get(querystring)


class ExchangeRateHandler(ResponseHandler):
    @staticmethod
    def handle(response):
        res = response.json()
        return ExchangeRateObject(res)


