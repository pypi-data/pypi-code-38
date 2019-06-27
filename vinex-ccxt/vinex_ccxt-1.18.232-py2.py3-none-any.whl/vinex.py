# -*- coding: utf-8 -*-

import hashlib
import hmac
import math
import time
from datetime import datetime

# from ccxt.base.errors import AuthenticationError, InvalidOrder
from ccxt.base.errors import ExchangeError
from ccxt.base.exchange import Exchange


class vinex (Exchange):

    def describe(self):
        return self.deep_extend(super(vinex, self).describe(), {
            'id': 'vinex',
            'name': 'Vinex',
            'countries': ['SG'],
            'rateLimit': 200,
            # 'has': {
            #     'fetchCurrencies': True,
            #     'fetchTickers': True,
            #     'fetchOpenOrders': True,
            #     'fetchMyTrades': True,
            #     'fetchDepositAddress': True,
            # },
            'urls': {
                'logo': 'https://storage.googleapis.com/vinex-images/mail-icons/vinex-logo.png',  # noqa
                'api': 'https://api.vinex.network/api/v2',
                'www': 'https://vinex.network/',
                'doc': 'https://docs.vinex.network/',
                # 'fees': 'https://vinex.network/fees',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'markets/{market_id}',
                        # 'currencies',
                        # 'tickers',
                        'get-ticker',
                        'get-order-book',
                        # 'get-orders',
                        # 'market/{market_id}/ohlcv/{interval}',
                    ],
                },
                'private': {
                    'get': [
                        'balances',
                        'get-my-orders',
                        'get-my-trading',
                        # 'user/order/{order_id}',
                        # 'user/market/{market_id}',
                        # 'user/withdraws',
                        # 'user/withdraw/{withdraw_id}',
                        # 'user/deposits',
                    ],
                    'post': [
                        'place-order',
                        'cancel-order',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.001,
                    'taker': 0.001,
                },
            },
        })

    def fetch_markets(self, params={}):
        markets = self.publicGetMarkets()['data']

        result = []

        for market in markets:
            id = market['symbol']

            quoteId, baseId = market['symbol'].split('_')

            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)

            symbol = base + '/' + quote
            active = market['status']

            precision = {
                'amount': market['decAmount'],
                'price': market['decPrice'],
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
                        'min': market['threshold'],
                        'max': None,
                    },
                },
                'info': market,
            })
        return result

    def parse_ticker(self, ticker, market=None):
        symbol = market['symbol']
        timestamp = ticker['date']
        ticker = ticker['ticker']

        last = self.safe_float(ticker, 'lastPrice')

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
            'high': self.safe_float(ticker, 'highPrice'),
            'low': self.safe_float(ticker, 'lowPrice'),
            'bid': self.safe_float(ticker, 'bidPrice'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'askPrice'),
            'askVolume': None,
            'vwap': None,
            # 'open': self.safe_float(ticker, 'day_open'),
            'close': last,
            'last': last,
            # 'previousClose': None,
            # 'change': change,
            # 'percentage': percentage,
            # 'average': self.safe_float(ticker, 'day_avg_price'),
            # 'baseVolume': self.safe_float(ticker, 'day_volume_market'),
            'quoteVolume': self.safe_float(ticker, 'quoteVolume'),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetGetTicker(self.extend({
            'market': market['id'],
        }, params))['data']

        ticker = {
            'date': self.milliseconds(),
            'ticker': ticker,
        }
        return self.parse_ticker(ticker, market)

    # def fetch_tickers(self, symbols=None, params={}):
    #     self.load_markets()
    #     tickers = self.publicGetTickers(params)['data']['markets']
    #     result = {}
    #     timestamp = self.milliseconds()

    #     for ticker in tickers:
    #         market = self.markets_by_id[ticker['id']]
    #         symbol = market['symbol']
    #         ticker = {
    #             'date': timestamp,
    #             'ticker': ticker,
    #         }
    #         result[symbol] = self.parse_ticker(ticker, market)
    #     return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()

        timestamp = self.milliseconds()

        orderbook = self.publicGetGetOrderBook(self.extend({
            'market': self.market_id(symbol),
        }, params))['data']

        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'quantity')

    def fetch_balance(self, params={}):
        self.load_markets()

        balances = self.privateGetBalances(params)['data']

        result = {'info': balances}

        for balance in balances:
            currency = self.common_currency_code(balance['asset'])

            free_amount = float(balance['free'])
            used_amount = float(balance['locked'])

            account = {
                'free': free_amount,
                'used': used_amount,
                'total': free_amount + used_amount,
            }

            result[currency] = account

        return self.parse_balance(result)

    def parse_trade(self, trade, market=None):
        # Common fields
        timestamp = trade['createdAt'] * 1000

        symbol = market['symbol']

        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'amount')

        # Result
        result = dict()

        result['datetime'] = self.iso8601(timestamp)
        result['timestamp'] = timestamp

        result['symbol'] = symbol

        result['price'] = price
        result['amount'] = amount
        result['info'] = trade.copy()

        # My trade info
        trade_id = self.safe_string(trade, 'id')
        if trade_id:
            result['id'] = trade_id
            result['order'] = self.safe_string(trade, 'idOrder')
            result['type'] = 'limit'

            if 'orderBuy' in trade:
                result['side'] = 'buy'
                fee = self.safe_float(trade['orderBuy'], 'fee')
            else:
                result['side'] = 'sell'
                fee = self.safe_float(trade['orderSell'], 'fee')

            cost = price * amount * fee
            fee_currency = market['quote']

            result['fee'] = {
                'cost': cost,
                'currency': fee_currency
            }

        return result

    # def fetch_trades(self, symbol, since=None, limit=None, params={}):
    #     self.load_markets()
    #     market = self.market(symbol)

    #     data = self.publicGetMarketMarketId(self.extend({
    #         'market_id': market['id'],
    #     }, params))['data']

    #     trades = list()
    #     for trade in data['recent_trades']:
    #         trade_obj = trade.copy()
    #         trade_obj['info'] = trade

    #         trades.append(trade_obj)

    #     return self.parse_trades(trades, market, since, limit)

    def parse_order(self, order, market=None):
        order_id = self.safe_string(order, 'uid')

        if 'market' in order:
            market = self.markets_by_id[order['market']]
        else:
            market = self.markets_by_id[order['pairSymbol']]

        symbol = market['symbol']

        timestamp = order['createdAt'] * 1000

        if 'action' in order:
            if order['action'] == 'BUY':
                side = 'buy'
            if order['action'] == 'SELL':
                side = 'sell'
        else:
            if order['actionType'] == 1:
                side = 'buy'
            elif order['actionType'] == 0:
                side = 'sell'

        if 'status' in order:
            if order['status'] == 10:
                status = 'open'
            elif order['status'] == 1:
                status = 'closed'
            elif order['status'] == 2:
                status = 'canceled'
        else:
            status = 'open'

        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'amount')

        if 'remaining' in order:
            remaining = self.safe_float(order, 'remain')
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
            'type': 'limit',
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
        request['market'] = market['id']

        # request['price'] = self.price_to_precision(symbol, price)
        # request['amount'] = self.amount_to_precision(symbol, amount)

        request['price'] = float(self.price_to_precision(symbol, price))
        request['amount'] = float(self.amount_to_precision(symbol, amount))

        if side == 'buy':
            request['type'] = 'BUY'
        elif side == 'sell':
            request['type'] = 'SELL'

        data = self.privatePostPlaceOrder(self.extend(request, params))['data']

        # if not data:
        #     raise InvalidOrder(self.id + ' ' + self.json(response))

        order_obj = data.copy()
        order_obj['info'] = data
        order = self.parse_order(order_obj)

        id = order['id']
        self.orders[id] = order

        return order

    def cancel_order(self, id, symbol=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        request = dict()
        request['market'] = market['id']
        request['uid'] = id

        result = self.privatePostCancelOrder(self.extend(request, params))

        return result

    # def fetch_order(self, id, symbol=None, params={}):
    #     self.load_markets()

    #     data = self.privateGetUserOrderOrderId(self.extend({
    #         'order_id': id
    #     }, params))['data']['order']

    #     order_obj = data.copy()
    #     order_obj['info'] = data

    #     order = self.parse_order(order_obj)

    #     return order

    def _parse_raw_orders(self, raw_orders, market, since, limit):
        order_objes = list()

        for order in raw_orders:
            order_obj = order.copy()
            order_obj['info'] = order

            order_objes.append(order_obj)

        return self.parse_orders(order_objes, market, since, limit)

    def _fetch_orders(self, symbol=None, since=None, limit=None, params={}, status=None):
        self.load_markets()

        request = dict()

        market = None
        if symbol:
            market = self.market(symbol)
            request['market'] = market['id']

        if since:
            request['start'] = since // 1000
        else:
            request['start'] = int(datetime.strptime('2018-01-01', '%Y-%m-%d').timestamp())

        if limit:
            request['limit'] = limit
        else:
            request['limit'] = 20

        if status:
            request['status'] = status

        raw_orders = self.privateGetGetMyOrders(self.extend(request, params))['data']

        return self._parse_raw_orders(raw_orders, market, since, limit)

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        return self._fetch_orders(symbol, since, limit, params)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        return self._fetch_orders(symbol, since, limit, params, status='OPENED')

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        return self._fetch_orders(symbol, since, limit, params, status='FINISHED')

    def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()

        request = dict()

        market = None
        if symbol:
            market = self.market(symbol)
            request['market'] = market['id']

        if since:
            request['start'] = since // 1000

        trades = self.privateGetGetMyTrading(self.extend(request, params))['data']

        return self.parse_trades(trades, market, since, limit)

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api']
        query = self.omit(params, self.extract_params(path))

        url += '/' + self.implode_params(path, params)

        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()

            headers = dict()
            headers['api-key'] = self.apiKey

            query['time_stamp'] = int(time.time())
            query['recv_window'] = 60                   # 60s

            if method == 'GET':
                if query:
                    url += '?' + self.urlencode(query)
            elif query:
                body = self.urlencode(query)

                if 'recv_window' in query:
                    if 'amount' in query:
                        msg = '{amount}_{market}_{price}_{recv_window}_{time_stamp}_{type}'.format(**query)
                    else:
                        msg = '{market}_{recv_window}_{time_stamp}_{uid}'.format(**query)
                else:
                    if 'amount' in query:
                        msg = '{amount}_{market}_{price}_{time_stamp}_{type}'.format(**query)
                    else:
                        msg = '{market}_{time_stamp}_{uid}'.format(**query)

                msg_hmac = hmac.new(self.secret.encode(), msg.encode(), hashlib.sha256)
                signature = msg_hmac.hexdigest()

                headers['signature'] = signature
                headers['Content-Type'] = 'application/x-www-form-urlencoded'

        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        try:
            response = self.fetch2(path, api, method, params, headers, body)
        except Exception as e:
            raise ExchangeError(e)

        # if response:
        #     success = self.safe_integer(response, 'success')
        #     if success == 0:
        #         message = self.safe_string(response, 'message')
        #         if message == 'Invalid APIKey':
        #             raise AuthenticationError(message)
        #         raise ExchangeError(message)

        return response
