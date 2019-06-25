from stockkly_repo import pricesBusiness
from pymongo import MongoClient
import datetime


class prices:
    def __init__(self, config):
        ''' Constructor for this class. '''
        conn = MongoClient(config['client'])
        self.conn = conn
        self.db = conn[config['db']]
        self.collection = self.db[config['collection']]

    def knock_knock(self):
        return "Who's there?"

    def get_price(self, ticker, price_date):
        price_date = datetime.datetime.strptime(
            price_date, "%Y-%m-%d")
        return self.collection.find_one({'ticker': ticker.upper(), 'priceDate': price_date})

    def get_price_now(self, ticker):
        price_date = datetime.datetime.strptime(
            str(datetime.datetime.now().date()), "%Y-%m-%d")

        return self.collection.find_one({'ticker': ticker.upper(), 'priceDate': price_date})

    def get_prices(self, ticker):
        return self.collection.find({'ticker': ticker.upper()})

    def upsert_price(self, ticker, price):

        price_date = datetime.datetime.strptime(
            str(datetime.datetime.now().date()), "%Y-%m-%d")

        data = self.build_data(ticker, price, price_date)

        return self.collection.update_one({'ticker': ticker.upper(), 'priceDate': price_date}, {"$set": data}, upsert=True)

    def upsert_price_with_data(self, ticker, data):
        # if data is None:
            # data = build_data(ticker, price, price_date)
        price_date = datetime.datetime.strptime(
            str(datetime.datetime.now().date()), "%Y-%m-%d")

        return self.collection.update_one({'ticker': ticker.upper(), 'priceDate': price_date}, {"$set": data}, upsert=True)

    def build_data(self, ticker, price, price_date):
        resval = self.collection.find_one(
            {'ticker': ticker.upper(), 'priceDate': price_date})
        if resval is None:
            data = {
                "ticker": ticker.upper(),
                "open": price,
                "price": price,
                "change": 0,
                "movement": 0,
                "priceDate": price_date
            }
        else:
            change = pricesBusiness.calc_change(price, resval['open'])
            # print("change is " + str(change))
            data = {
                "ticker": ticker.upper(),
                "open": resval['open'],
                "price": price,
                "change": change,
                "movement": pricesBusiness.calc_movement(change, price),
                "priceDate": price_date
            }
        return data
