from __future__ import print_function
import pendulum
import requests
import furl

from .constant import BASE_API_URL


class Public:

    def __init__(self, url=None):
        self.url = url if url is not None else BASE_API_URL

    def ping(self):
        """ See https://apidocs.stex.com/#/Public/get_public_ping """
        return self.send_request(self.url + '/public/ping')

    def currencies(self):
        """ See https://apidocs.stex.com/#/Public/get_public_currencies """
        return self.send_request(self.url + '/public/currencies')

    def currencies_by_id(self, currency_id):
        """ See https://apidocs.stex.com/#/Public/get_public_currencies__currencyId_ """
        return self.send_request(self.url + '/public/currencies/' + str(currency_id))

    def markets(self):
        """ See https://apidocs.stex.com/#/Public/get_public_markets """
        return self.send_request(self.url + '/public/markets')

    def pairs_groups(self):
        """ See https://apidocs.stex.com/#/Public/get_public_pairs_groups """
        return self.send_request(self.url + '/public/pairs-groups')

    def currency_pairs_list(self, code=None):
        """ See https://apidocs.stex.com/#/Public/get_public_currency_pairs_list__code_ """
        if code is None:
            code = 'ALL'
        return self.send_request(self.url + '/public/currency_pairs/list/' + code)

    def pairs_groups_by_id(self, currency_pair_group_id):
        """ See https://apidocs.stex.com/#/Public/get_public_currency_pairs_group__currencyPairGroupId_ """
        return self.send_request(self.url + '/public/currency_pairs/group/' + str(currency_pair_group_id))

    def currency_pairs_by_id(self, currency_pair_id):
        """ See https://apidocs.stex.com/#/Public/get_public_currency_pairs__currencyPairId_ """
        return self.send_request(self.url + '/public/currency_pairs/' + str(currency_pair_id))

    def ticker(self):
        """ See https://apidocs.stex.com/#/Public/get_public_ticker """
        return self.send_request(self.url + '/public/ticker')

    def ticker_by_currency_pair_id(self, currency_pair_id):
        """ See https://apidocs.stex.com/#/Public/get_public_ticker__currencyPairId_ """
        return self.send_request(self.url + '/public/ticker/' + str(currency_pair_id))

    def trades_by_currency_pair_id(self, currency_pair_id, params=None):
        """ See https://apidocs.stex.com/#/Public/get_public_trades__currencyPairId_ """
        if params is None:
            params = {}
        f = furl.furl(self.url + '/public/trades/' + str(currency_pair_id)).add(params)
        return self.send_request(f.url)

    def orderbook_by_currency_pair_id(self, currency_pair_id, params=None):
        """ See https://apidocs.stex.com/#/Public/get_public_orderbook__currencyPairId_"""
        if params is None:
            params = {}
        f = furl.furl(self.url + '/public/orderbook/' + str(currency_pair_id)).add(params)
        return self.send_request(f.url)

    def chart(self, currency_pair_id, candles_type='1D', time_start=None, time_end=None, params=None):
        """ See https://apidocs.stex.com/#/Public/get_public_chart__currencyPairId___candlesType_ """
        now = pendulum.now('UTC')
        if params is None:
            params = {}
        if time_start is None:
            params['timeStart'] = now.subtract(weeks=1).int_timestamp
        if time_end is None:
            params['timeEnd'] = now.int_timestamp
        f = furl.furl(self.url + '/public/chart/' + str(currency_pair_id) + '/' + candles_type).add(params)
        return self.send_request(f.url)

    @staticmethod
    def send_request(url):
        try:
            r = requests.get(url)
            return r.json()
        except Exception as e:
            return e
