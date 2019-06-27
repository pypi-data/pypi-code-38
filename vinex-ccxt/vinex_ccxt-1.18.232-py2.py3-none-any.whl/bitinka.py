# -*- coding: utf-8 -*-

from ccxt.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import InvalidNonce

class bitinka(Exchange):
    def describe(self):
        return self.deep_extend(super(bitinka, self).describe(), {
            'id': 'bitinka',
            'name': 'Bitinka',
            'countries': ['MT', 'EU'],  # Malta
            'rateLimit': 1000,
            'has': {
                'CORS': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://www.bitinka.com/img/new_img/bitinka_original.svg',
                'www': 'https://www.bitinka.com',
                'api': {
                    'public': 'https://www.bitinka.com/api/apinka',
                    'private': 'https://www.bitinka.com/api/apinka',
                },
                'doc': [
                    'https://www.bitinka.com/uk/bitinka/api_documentation'
                ],
                'fees': '',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'ticker',
                        'ticker/{pair}',
                        'order_book/{pair}'
                    ],
                },
                'private': {
                    'post': [
                        'get_balance/format/json',
                        'get_wallet_balance/format/json',
                        'create_order/format/json',
                        'create_order/stop/format/json',
                        'cancel_order/format/json',
                        'orders_user/format/json'
                    ],
                },
            },
            'markets': {
                'BTC/ARS': {'id': 'BTC_ARS', 'symbol': 'BTC/ARS', 'base': 'BTC', 'quote': 'ARS', 'baseId': 'BTC', 'quoteId': 'ARS'},
                'BTC/BOB': {'id': 'BTC_BOB', 'symbol': 'BTC/BOB', 'base': 'BTC', 'quote': 'BOB', 'baseId': 'BTC', 'quoteId': 'BOB'},
                'BTC/BRL': {'id': 'BTC_BRL', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'baseId': 'BTC', 'quoteId': 'BRL'},
                'BTC/CLP': {'id': 'BTC_CLP', 'symbol': 'BTC/CLP', 'base': 'BTC', 'quote': 'CLP', 'baseId': 'BTC', 'quoteId': 'CLP'},
                'BTC/CNY': {'id': 'BTC_CNY', 'symbol': 'BTC/CNY', 'base': 'BTC', 'quote': 'CNY', 'baseId': 'BTC', 'quoteId': 'CNY'},
                'BTC/COP': {'id': 'BTC_COP', 'symbol': 'BTC/COP', 'base': 'BTC', 'quote': 'COP', 'baseId': 'BTC', 'quoteId': 'COP'},
                'BTC/EUR': {'id': 'BTC_EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR', 'baseId': 'BTC', 'quoteId': 'EUR'},
                'BTC/PEN': {'id': 'BTC_EUR', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR', 'baseId': 'BTC', 'quoteId': 'EUR'},
                'LTC/BTC': {'id': 'LTC_BTC', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'baseId': 'LTC', 'quoteId': 'BTC'},
                'XRP/BTC': {'id': 'XRP_BTC', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC', 'baseId': 'XRP', 'quoteId': 'BTC'},
                'DASH/BTC': {'id': 'DASH_BTC', 'symbol': 'DASH/BTC', 'base': 'DASH', 'quote': 'BTC', 'baseId': 'DASH', 'quoteId': 'BTC'},
                'ACT/BTC': {'id': 'ACT_BTC', 'symbol': 'ACT/BTC', 'base': 'ACT', 'quote': 'BTC', 'baseId': 'ACT', 'quoteId': 'BTC'},
                'VEX/BTC': {'id': 'VEX_BTC', 'symbol': 'VEX/BTC', 'base': 'VEX', 'quote': 'BTC', 'baseId': 'VEX', 'quoteId': 'BTC'},
                'NEO/BTC': {'id': 'NEO_BTC', 'symbol': 'NEO/BTC', 'base': 'NEO', 'quote': 'BTC', 'baseId': 'NEO', 'quoteId': 'BTC'},
                'GAS/BTC': {'id': 'GAS_BTC', 'symbol': 'GAS/BTC', 'base': 'GAS', 'quote': 'BTC', 'baseId': 'GAS', 'quoteId': 'BTC'},
                'SSP/BTC': {'id': 'SSP_BTC', 'symbol': 'SSP/BTC', 'base': 'SSP', 'quote': 'SSP', 'baseId': 'SSP', 'quoteId': 'BTC'},
                'SSC/BTC': {'id': 'SSC_BTC', 'symbol': 'SSC/BTC', 'base': 'SSC', 'quote': 'BTC', 'baseId': 'SSC', 'quoteId': 'BTC'},
                'BTG/BTC': {'id': 'BTG_BTC', 'symbol': 'BTG/BTC', 'base': 'BTG', 'quote': 'BTC', 'baseId': 'BTG', 'quoteId': 'BTC'},
                'BCH/BTC': {'id': 'BCH_BTC', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'baseId': 'BCH', 'quoteId': 'BTC'},
                'NANO/BTC': {'id': 'NANO_BTC', 'symbol': 'NANO/BTC', 'base': 'NANO', 'quote': 'BTC', 'baseId': 'NANO', 'quoteId': 'BTC'},
                'ETH/BTC': {'id': 'ETH_BTC', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'baseId': 'ETH', 'quoteId': 'BTC'},
                'ETH/ARS': {'id': 'ETH_ARS', 'symbol': 'ETH/ARS', 'base': 'ETH', 'quote': 'ARS', 'baseId': 'ETH', 'quoteId': 'ARS'},
                'ETH/BOB': {'id': 'ETH_BOB', 'symbol': 'ETH/BOB', 'base': 'ETH', 'quote': 'BOB', 'baseId': 'ETH', 'quoteId': 'BOB'},
                'ETH/BRL': {'id': 'ETH_BRL', 'symbol': 'ETH/BRL', 'base': 'ETH', 'quote': 'BRL', 'baseId': 'ETH', 'quoteId': 'BRL'},
                'ETH/CLP': {'id': 'ETH_CLP', 'symbol': 'ETH/CLP', 'base': 'ETH', 'quote': 'CLP', 'baseId': 'ETH', 'quoteId': 'CLP'},
                'ETH/CNY': {'id': 'ETH_CNY', 'symbol': 'ETH/CNY', 'base': 'ETH', 'quote': 'CNY', 'baseId': 'ETH', 'quoteId': 'CNY'},
                'ETH/COP': {'id': 'ETH_COP', 'symbol': 'ETH/COP', 'base': 'ETH', 'quote': 'COP', 'baseId': 'ETH', 'quoteId': 'COP'},
                'ETH/EUR': {'id': 'ETH_EUR', 'symbol': 'ETH/EUR', 'base': 'ETH', 'quote': 'EUR', 'baseId': 'ETH', 'quoteId': 'EUR'},
                'ETH/PEN': {'id': 'ETH_PEN', 'symbol': 'ETH/PEN', 'base': 'ETH', 'quote': 'PEN', 'baseId': 'ETH', 'quoteId': 'PEN'},
                'LTC/ETH': {'id': 'LTC_ETH', 'symbol': 'LTC/ETH', 'base': 'LTC', 'quote': 'ETH', 'baseId': 'LTC', 'quoteId': 'ETH'},
                'DASH/ETH': {'id': 'DASH_ETH', 'symbol': 'DASH/ETH', 'base': 'ETH', 'quote': 'DASH', 'baseId': 'DASH', 'quoteId': 'ETH'},
                'ACT/ETH': {'id': 'ACT_ETH', 'symbol': 'ACT/ETH', 'base': 'ACT', 'quote': 'ETH', 'baseId': 'ACT', 'quoteId': 'ETH'},
                'VEX/ETH': {'id': 'VEX_ETH', 'symbol': 'VEX/ETH', 'base': 'VEX', 'quote': 'ETH', 'baseId': 'VEX', 'quoteId': 'ETH'},
                'NEO/ETH': {'id': 'NEO_ETH', 'symbol': 'NEO/ETH', 'base': 'NEO', 'quote': 'ETH', 'baseId': 'NEO', 'quoteId': 'ETH'},
                'GAS/ETH': {'id': 'GAS_ETH', 'symbol': 'GAS/ETH', 'base': 'GAS', 'quote': 'ETH', 'baseId': 'GAS', 'quoteId': 'ETH'},
                'SSP/ETH': {'id': 'SSP_ETH', 'symbol': 'SSP/ETH', 'base': 'SSP', 'quote': 'ETH', 'baseId': 'SSP', 'quoteId': 'ETH'},
                'SSC/ETH': {'id': 'SSC_ETH', 'symbol': 'SSC/ETH', 'base': 'SSC', 'quote': 'SSC', 'baseId': 'SSC', 'quoteId': 'ETH'},
                'BTG/ETH': {'id': 'BTG_ETH', 'symbol': 'BTG/ETH', 'base': 'BTG', 'quote': 'ETH', 'baseId': 'BTG', 'quoteId': 'ETH'},
                'BCH/ETH': {'id': 'BCH_ETH', 'symbol': 'BCH/ETH', 'base': 'BCH', 'quote': 'ETH', 'baseId': 'BCH', 'quoteId': 'ETH'},
                'NANO/ETH': {'id': 'NANO_ETH', 'symbol': 'NANO/ETH', 'base': 'NANO', 'quote': 'ETH', 'baseId': 'NANO', 'quoteId': 'ETH'},
                'XRP/ETH': {'id': 'XRP_ETH', 'symbol': 'XRP/ETH', 'base': 'XRP', 'quote': 'ETH', 'baseId': 'XRP', 'quoteId': 'ETH'},
                'BTC/USD': {'id': 'BTC_USD', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'baseId': 'BTC','quoteId': 'USD'},
                'ETH/USD': {'id': 'ETH_USD', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD', 'baseId': 'ETH', 'quoteId': 'USD'},
                'DASH/USD': {'id': 'DASH_USD', 'symbol': 'DASH/USD', 'base': 'DASH', 'quote': 'USD', 'baseId': 'DASH', 'quoteId': 'USD'},
                'LTC/USD': {'id': 'LTC_USD', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD', 'baseId': 'LTC', 'quoteId': 'USD'},
                'XRP/USD': {'id': 'XRP_USD', 'symbol': 'XRP/USD', 'base': 'XRP', 'quote': 'USD', 'baseId': 'XRP', 'quoteId': 'USD'},
                'ACT/USD': {'id': 'ACT_USD', 'symbol': 'ACT/USD', 'base': 'ACT', 'quote': 'USD', 'baseId': 'ACT', 'quoteId': 'USD'},
                'VEX/USD': {'id': 'VEX_USD', 'symbol': 'VEX/USD', 'base': 'VEX', 'quote': 'USD', 'baseId': 'VEX', 'quoteId': 'USD'},
                'NEO/USD': {'id': 'NEO_USD', 'symbol': 'NEO/USD', 'base': 'NEO', 'quote': 'USD', 'baseId': 'NEO', 'quoteId': 'USD'},
                'GAS/USD': {'id': 'GAS_USD', 'symbol': 'GAS/USD', 'base': 'GAS', 'quote': 'USD', 'baseId': 'GAS', 'quoteId': 'USD'},
            },
            'fees': {
                'trading': {
                    'maker': 0.3 / 100,
                    'taker': 0.0043,
                },
                'funding': {
                    'withdraw': {
                        'BTC': 0.0009,
                        'LTC': 0.005,
                        'ETH': 0.00126,
                        'LSK': 0.2,
                        'BCH': 0.0006,
                        'GAME': 0.005,
                        'DASH': 0.001,
                        'BTG': 0.0008,
                        'PLN': 4,
                        'EUR': 1.5,
                    },
                },
            },
            'exceptions': {
                '400': ExchangeError,  # At least one parameter wasn't set
                '401': InvalidOrder,  # Invalid order type
                '402': InvalidOrder,  # No orders with specified currencies
                '403': InvalidOrder,  # Invalid payment currency name
                '404': InvalidOrder,  # Error. Wrong transaction type
                '405': InvalidOrder,  # Order with self id doesn't exist
                '406': InsufficientFunds,  # No enough money or crypto
                '408': InvalidOrder,  # Invalid currency name
                '501': AuthenticationError,  # Invalid public key
                '502': AuthenticationError,  # Invalid sign
                '503': InvalidNonce,  # Invalid moment parameter. Request time doesn't match current server time
                '504': ExchangeError,  # Invalid method
                '505': AuthenticationError,  # Key has no permission for self action
                '506': AuthenticationError,  # Account locked. Please contact with customer service
                '509': ExchangeError,  # The BIC/SWIFT is required for self currency
                '510': ExchangeError,  # Invalid market name
            },
        })


    def fetch_market(self, params={"format": "json"}):
        markets = self.publicGetMarkets(self.extend({}, params))
        return markets

    def fetch_ticker(self, params={"format": "json"}):
        tickers = self.publicGetTicker(self.extend({}, params))
        return tickers

    def fetch_ticker_per_pair(self, pair, params={"format": "json"}):
        ticker = self.publicGetTickerPair(self.extend({'pair': self.market_id(pair)}, params))
        return ticker

    def fetch_order_book(self, pair, params={"format": "json"}):
        order_book = self.publicGetOrderBookPair(self.extend({'pair': self.market_id(pair)}, params))
        return order_book

    def post_trade_balance(self, key, secret, params={}):
        trade_balance = self.privatePostGetBalanceFormatJson(self.extend({'key': key, 'secret': secret}, params))
        return trade_balance

    def post_get_balance(self, key, secret, params={}):
        get_balance = self.privatePostGetWalletBalanceFormatJson(self.extend({'key': key, 'secret': secret}, params))
        return get_balance

    def create_order(self, key, secret, new, params={}):
        if not new.typeOrder or not new.price or not new.investement or not new.firstCurrency or not new.secondCurrency or not new.trade:
            raise ExchangeError('new have key: typeOrder, price, investement, firstCurrency, secondCurrency, trade')
        return self.privatePostCreateOrderFormatJson(self.extend({
            'key': key,
            'secret': secret,
            'new': new,
        }, params))

    def create_order_stop(self, key, secret, new, params={}):
        if not new.typeOrder or not new.price or not new.investement or not new.firstCurrency or not new.secondCurrency or not new.trade or not new.percentage:
            raise ExchangeError('new have key: typeOrder, price, investement, firstCurrency, secondCurrency, trade, percentage')
        return self.privatePostCreateOrderStopFormatJson(self.extend({
            'key': key,
            'secret': secret,
            'new': new,
        }, params))

    def cancel_order(self, key, secret, pair, params={}):
        return self.privatePostCancelOrderFormatJson(self.extend({
            'key': key,
            'secret': secret,
            'new': self.market_id(pair),
        }, params))

    def order_user(self, key, secret, firstCurrency, secondCurrency, trade, params={}):
        return self.privatePostOrderUserFormatJson(self.extend({
            'key': key,
            'secret': secret,
            'firstCurrency': firstCurrency,
            'secondCurrency': secondCurrency,
            'trade': trade
        }, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        if api == 'public':
            query = self.omit(params, self.extract_params(path))
            url += '/' + self.implode_params(path, params)
            url += '?' + self.urlencode(query)
        elif api == 'private':
            # self.check_required_credentials()
            query = self.omit(params, self.extract_params(path))
            headers = {
                'X-MBX-APIKEY': self.apiKey,
            }
            url += '/' + self.implode_params(path, params)
            if (method == 'GET') or (method == 'DELETE'):
                url += '?' + query
            else:
                body = self.json(query)
                headers['Content-Type'] = 'application/json'
        else:
            if params:
                url += '?' + self.urlencode(params)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}


    def handle_errors(self, httpCode, reason, url, method, headers, body, response):
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            if 'status' in response:
                status = self.safe_string(response, 'status')
                message = self.safe_string(response, 'message')
                if status is not None:
                    if status == '0000':
                        return  # no error
                    feedback = self.id + ' ' + self.json(response)
                    exceptions = self.exceptions
                    if status in exceptions:
                        raise exceptions[status](feedback)
                    elif message in exceptions:
                        raise exceptions[message](feedback)
                    else:
                        raise ExchangeError(feedback)