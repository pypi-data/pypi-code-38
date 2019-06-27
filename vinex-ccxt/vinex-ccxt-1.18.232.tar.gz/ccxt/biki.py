# -*- coding: utf-8 -*-

import hashlib
import math
import random
import time

from ccxt.base.errors import ExchangeError, InvalidOrder
from ccxt.base.exchange import Exchange


class biki (Exchange):

    def describe(self):
        return self.deep_extend(super(biki, self).describe(), {
            'id': 'biki',
            'name': 'biki',
            'countries': ['CN'],
            'rateLimit': 400,
            'urls': {
                'logo': 'https://bikicoin.oss-cn-hangzhou.aliyuncs.com/web_doc/Footerimage/logopath.png',
                'api': 'https://api.biki.com',
                'www': 'https://biki.com/',
                'doc': 'https://github.com/code-bikicoin/bikicoin/blob/master/api/us_en/api_doc_en.md',
                'fees': 'https://support.biki.com/hc/en-us/articles/360019543671-BikiCoin-Fees',
                'referral': 'https://www.biki.com/register?inviteCode=EEAEWTA',
            },
            'api': {
                'public': {
                    'get': [
                        'open/api/common/symbols',      # symbols info
                        'open/api/get_ticker',          # ticker
                        # 'open/api/get_allticker',       # tickers
                        'open/api/get_trades',          # orderbook
                    ],
                },
                'private': {
                    'get': [
                        'open/api/user/account',        # user balance
                        # 'user/orders',
                        'open/api/order_info',          # get order
                        'open/api/v2/all_order',        # get orders: by symbol
                        'open/api/v2/new_order',        # get open orders: by symbol
                        'open/api/all_trade',           # get my trades: by symbol
                    ],
                    'post': [
                        'open/api/create_order',        # create order
                        'open/api/cancel_order',        # cancel order
                        'open/api/cancel_order_all',    # cancel all order
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.0015,
                    'taker': 0.0015,
                },
            },
        })

    ####################################
    # Public:
    ####################################
    def fetch_markets(self, params={}):
        markets = self.publicGetOpenApiCommonSymbols()['data']

        result = []

        for market in markets:
            id = market['symbol']

            baseId = market['base_coin']
            quoteId = market['count_coin']

            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)

            symbol = base + '/' + quote
            active = True

            precision = {
                'amount': market['amount_precision'],
                'price': market['price_precision'],
            }

            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': active,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': math.pow(10, -precision['amount']),
                        'max': math.pow(10, precision['amount']),
                    },
                    'price': {
                        'min': math.pow(10, -precision['price']),
                        'max': math.pow(10, precision['price']),
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                },
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market=None):
        symbol = market['symbol']
        timestamp = ticker['time']
        last = self.safe_float(ticker, 'last')

        # open_price = self.safe_float(ticker, 'open')
        # if last and open_price:
        #     change = last - open_price
        # else:
        #     change = None

        # if self.safe_float(ticker, 'day_change'):
        #     percentage = self.safe_float(ticker, 'day_change') * 100
        # else:
        #     percentage = None

        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'high'),
            'low': self.safe_float(ticker, 'low'),
            'bid': self.safe_float(ticker, 'buy'),
            # 'bidVolume': None,
            'ask': self.safe_float(ticker, 'sell'),
            # 'askVolume': None,
            # 'vwap': None,
            # 'open': self.safe_float(ticker, 'open'),
            'close': last,
            'last': last,
            # 'previousClose': None,
            # 'change': change,
            # 'percentage': percentage,
            # 'average': self.safe_float(ticker, 'day_avg_price'),
            'baseVolume': self.safe_float(ticker, 'vol'),
            # 'quoteVolume': self.safe_float(ticker, 'vol'),    # NOTE: This API don't have quoteVolume info
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)

        ticker = self.publicGetOpenApiGetTicker(self.extend({
            'symbol': market['id'],
        }, params))['data']

        return self.parse_ticker(ticker, market)

    # # TODO: fetch_tickers()
    # def fetch_tickers(self, symbols=None, params={}):
    #     pass

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()

        timestamp = self.milliseconds()

        orderbook = self.publicGetOpenApiGetTrades(self.extend({
            'symbol': self.market_id(symbol),
        }, params))['data']

        buy_orders = list()
        sell_orders = list()

        for order in orderbook:
            if order['type'] == 'buy':
                buy_orders.append(order)
            elif order['type'] == 'sell':
                sell_orders.append(order)

        result = dict()
        result['buy'] = sorted(buy_orders, key=lambda t: t['price'], reverse=True)
        result['sell'] = sorted(sell_orders, key=lambda t: t['price'])

        return self.parse_order_book(result, timestamp, 'buy', 'sell', 'price', 'amount')

    # TODO: parse_trade()
    def parse_trade(self, trade, market=None):
        pass

    # # TODO: fetch_trades()
    # def fetch_trades(self, symbol, since=None, limit=None, params={}):
    #     pass

    # ####################################
    # # Private:
    # ####################################
    def fetch_balance(self, params={}):
        self.load_markets()

        balances = self.privateGetOpenApiUserAccount(params)['data']['coin_list']

        result = {'info': balances}

        for balance in balances:
            if float(balance['btcValuatin']) == 0:
                continue

            currency = self.common_currency_code(balance['coin'].upper())

            free_amount = float(balance['normal'])
            used_amount = float(balance['locked'])

            account = {
                'free': free_amount,
                'used': used_amount,
                'total': free_amount + used_amount,
            }

            result[currency] = account

        return self.parse_balance(result)

    def parse_order(self, order, market=None):
        order_id = self.safe_string(order, 'id')

        symbol = f"{order['baseCoin']}/{order['countCoin']}".upper()

        timestamp = order['created_at']

        if order['side'] == 'BUY':
            side = 'buy'
        if order['side'] == 'SELL':
            side = 'sell'

        if order['type'] == 1:
            order_type = 'limit'
        elif order['type'] == 2:
            order_type = 'market'

        if order['status'] == 0 or order['status'] == 1 or order['status'] == 3:
            status = 'open'
        elif order['status'] == 2:
            status = 'closed'
        elif order['status'] == 4:
            status = 'canceled'
        else:  # other status: pending cancel, expired
            status = 'other'

        price = self.safe_float(order, 'total_price')
        amount = self.safe_float(order, 'volume')

        if 'remaining' in order:
            remaining = self.safe_float(order, 'remain_volume')
        else:
            remaining = amount

        filled = amount - remaining
        cost = filled * price

        return {
            'id': order_id,
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': order_type,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'cost': cost,
            'info': order['info'],
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        request = dict()
        request['symbol'] = market['id']

        request['price'] = self.price_to_precision(symbol, price)
        request['volume'] = self.amount_to_precision(symbol, amount)

        if side == 'buy':
            request['side'] = 'BUY'
        elif side == 'sell':
            request['side'] = 'SELL'

        if type == 'limit':
            request['type'] = 1
        elif type == 'market':
            request['type'] = 2

        resp = self.privatePostOpenApiCreateOrder(self.extend(request, params))

        if not resp['data']:
            raise InvalidOrder(self.json(resp))

        order_id = resp['data']['order_id']
        return order_id

        # order_obj = data.copy()
        # order_obj['info'] = data
        # order = self.parse_order(order_obj)

        # id = order['id']
        # self.orders[id] = order

        # return order

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        request = dict()
        request['symbol'] = market['id']
        request['order_id'] = id

        result = self.privatePostOpenApiCancelOrder(self.extend(request, params))

        return result

    def cancel_all_order(self, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        request = dict()
        request['symbol'] = market['id']

        result = self.privatePostOpenApiCancelOrderAll(self.extend(request, params))

        return result

    # # TODO: fetch_order()
    # def fetch_order(self, id, symbol=None, params={}):
    #     pass

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()

        market = self.market(symbol)

        raw_orders = self.privateGetOpenApiV2AllOrder(self.extend({
            'symbol': market['id'],
            'pageSize': 10000
        }, params))['data']['orderList']

        order_objes = list()

        for order in raw_orders:
            order_obj = order.copy()
            order_obj['info'] = order

            order_objes.append(order_obj)

        return self.parse_orders(order_objes, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        total_orders = self.fetch_orders(symbol, since, limit, params)
        open_orders = self.filter_by(total_orders, 'status', 'open')

        return open_orders

    # # TODO: fetch_my_trades()
    # def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
    #     pass

    ####################################
    # Base:
    ####################################
    def _url_encode_params(self, query):
        query_text = ''
        for key, value in sorted(query.items()):
            query_text += f'{key}={value}&'
        query_text = query_text[:-1]

        return query_text

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api']
        query = self.omit(params, self.extract_params(path))

        url += '/' + self.implode_params(path, params)

        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            timestamp = int(time.time())

            query['api_key'] = self.apiKey
            query['time'] = timestamp

            query_text = self._url_encode_params(query)

            msg = ''

            for key, value in sorted(query.items()):
                msg += f'{key}{value}'

            signature = hashlib.md5(f'{msg}{self.secret}'.encode()).hexdigest()

            query['sign'] = signature

            if query:
                url += f'?{query_text}&sign={signature}'

            # if method == 'GET':
            # elif query:
            #     body = self.json(query)

        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        MAX_RETRY = 3

        count = 0

        while count < MAX_RETRY:
            try:
                response = self.fetch2(path, api, method, params, headers, body)
            except Exception as e:
                raise ExchangeError(e)

            # RateLimit
            if response['code'] == '110041':
                # Wait
                sleep_time = 0.5 + random.random() * (count + 1)
                time.sleep(sleep_time)

                count += 1
            else:
                break

        if response['code'] == '110041':
            raise ExchangeError(f'Rate Limit: {response}')

        return response
