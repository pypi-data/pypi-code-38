"""
This project wants to be a wrapper to use https://iexcloud.com/ API in a simple way
"""

import requests
from urllib import parse
from IEXWrapper.exceptions import InvalidAccountPeriod, InvalidTimeFrame, InvalidGroups
from config import IEX_AVAILABLE_GROUPS, IEX_BASE_URL, IEX_BASE_URL_TEST, IEX_AVAILABLE_RANGES, IEX_PRIVATE_TOKEN, \
                   IEX_PUBLIC_TOKEN, IEX_TEST_PRIVATE_TOKEN, IEX_TEST_PUBLIC_TOKEN, IEX_BATCH_ENDPOINT


class IEXTrading:
    # constructor
    def __init__(self, symbols: str = '', test=False):
        self.ticker = self._format_list(symbols.lower() if isinstance(symbols, str) else [t.lower() for t in symbols])
        self.request_counter = 0
        self._batch_endpoint = IEX_BATCH_ENDPOINT
        self._available_groups = IEX_AVAILABLE_GROUPS
        self._available_ranges = IEX_AVAILABLE_RANGES
        self._available_accounts = ['annual', 'quarter']
        if test:
            self.pk_token = IEX_TEST_PUBLIC_TOKEN
            self.sk_token = IEX_TEST_PRIVATE_TOKEN
            self.base_url = IEX_BASE_URL_TEST
        else:
            self.pk_token = IEX_PUBLIC_TOKEN
            self.sk_token = IEX_PRIVATE_TOKEN
            self.base_url = IEX_BASE_URL

        if len(self.ticker.split(',')) > 100:
            raise ValueError('IEX Cloud support maximum 100 symbols in a single call.')

    @staticmethod
    def _format_list(obj):
        # This method format lists in url format (ex. ['AAPL', 'MSFT'] --> 'AAPL,MSFT')
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, list):
            return str(','.join(obj))
        else:
            raise ValueError('ticker missing')

    def _make_request(self, endpoint, parameters: dict = None):
        parameters = {'token': self.pk_token} if parameters is None else dict(parameters, **{'token': self.pk_token})
        return self._call_server(self.base_url + endpoint, params=parameters)

    def _call_server(self, url, params: dict =None):
        resp = requests.get(url, params=params)

        if resp.status_code == 200:
            self.request_counter += 1
            print(resp.url)
            return resp.json()
        else:
            raise ConnectionError('IEX Trading API response code was: {} - {} URL: {}'\
                                  .format(resp.status_code, resp.reason, resp.url))

    def _make_batch_request(self, type: str):
        endpoint = self._batch_endpoint.format(self.ticker, type)
        return self._make_request(endpoint)

    def _make_multiple_requests(self, base_endpoint: str, parameters: dict = None):
        res = []
        for stock in self.ticker.split(','):
            res.append(self._make_request(base_endpoint.format(stock), parameters=parameters))
        return res

    def available_stocks(self):
        return self._make_request('/ref-data/symbols')

    def get_stock_quote(self):
        return self._make_batch_request('quote')

    def get_news(self):
        return self._make_batch_request('news')

    def get_book(self):
        return self._make_batch_request('book')

    def get_chart(self, range):
        if range in self._available_ranges:
            return self._make_batch_request('chart&range={}'.format(range))
        else:
            raise InvalidTimeFrame()

    # Returns an array of quotes for the top 10 symbols in a specified list.
    def get_list_value(self, group):
        if group in self._available_groups:
            endpoint = f'/stock/market/{group}'
            return self._make_request(endpoint)
        else:
            raise InvalidGroups()

    def get_sector_performance(self):
        return self._make_request('/stock/market/sector-performance')

    def get_company_info(self):
        return self._make_batch_request('company')

    def get_companies_by_sector(self, sector_name):
        endpoint = '/stock/market/collection/sector?collectionName={}'.format(parse.quote_plus(sector_name))
        return self._make_request(endpoint)

    def get_companies_by_tag(self, tag_name):
        endpoint = '/stock/market/collection/tag?collectionName={}'.format(parse.quote_plus(tag_name))
        return self._make_request(endpoint)

    def get_stock_dividend(self, range):
        if range in self._available_ranges:
            base_endpoint = '/stock/{}/dividends/'+range
            return self._make_multiple_requests(base_endpoint)
        else:
            raise InvalidTimeFrame()

    def get_earnings(self):
        return self._make_batch_request('earnings')

    def get_custom_call(self, endpoint):
        return self._make_request(endpoint)

    def get_financial_overview(self, period):
        if period.lower() in self._available_accounts:
            endpoint = '/stock/{}/financials?period={}'.format(self.ticker, period)
            return self._make_request(endpoint)
        else:
            raise InvalidAccountPeriod()

    def get_key_stats(self):
        endpoint = '/stock/{}/stats'.format(self.ticker)
        return self._make_request(endpoint)

    def get_balance_sheet(self, period):
        if period.lower() in self._available_accounts:
            base_endpoint = '/stock/{}/balance-sheet'
            return self._make_multiple_requests(base_endpoint=base_endpoint, parameters={'period': period})
        else:
            raise InvalidAccountPeriod()

    def get_cash_flow(self, period):
        if period.lower() in self._available_accounts:
            base_endpoint = '/stock/{}/cash-flow'
            return self._make_multiple_requests(base_endpoint=base_endpoint, parameters={'period': period})
        else:
            raise InvalidAccountPeriod()

    def get_income_statement(self, period):
        if period.lower() in self._available_accounts:
            base_endpoint = '/stock/{}/income'
            return self._make_multiple_requests(base_endpoint=base_endpoint, parameters={'period': period})
        else:
            raise InvalidAccountPeriod()

    def get_splits(self, range: str):
        if range in self._available_ranges:
            base_endpoint = '/stock/{}/splits/'+range
            return self._make_multiple_requests(base_endpoint=base_endpoint)
        else:
            raise InvalidTimeFrame()

    def get_estimates_eps(self):
        endpoint = '/stock/{}/estimates'.format(self.ticker)
        return self._make_request(endpoint)

    def get_ohlc(self):
        return self._make_batch_request('ohlc')

    def get_previous(self):
        return self._make_batch_request('previous')
