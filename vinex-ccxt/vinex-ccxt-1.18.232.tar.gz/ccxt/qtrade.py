# -*- coding: utf-8 -*-

import base64
import hashlib
import math
import time
from datetime import datetime

# from ccxt.base.errors import AuthenticationError, InvalidOrder
from ccxt.base.errors import ExchangeError
from ccxt.base.exchange import Exchange


class qtrade (Exchange):

    def describe(self):
        return self.deep_extend(super(qtrade, self).describe(), {
            'id': 'qtrade',
            'name': 'qTrade',
            'countries': ['US'],
            'rateLimit': 100,
            # 'has': {
            #     'fetchCurrencies': True,
            #     'fetchTickers': True,
            #     'fetchOpenOrders': True,
            #     'fetchMyTrades': True,
            #     'fetchDepositAddress': True,
            # },
            'urls': {
                'logo': 'hhttps://qtrade.io/images/logo.png',
                'api': 'https://api.qtrade.io/v1',
                'www': 'https://qtrade.io/',
                'doc': 'https://qtrade-exchange.github.io/qtrade-docs/',
                'fees': 'https://qtrade.io/fees',
                'referral': 'https://qtrade.io/?ref=AZCXUQ6P5KCG',
            },
            'api': {
                'public': {
                    'get': [
                        'markets',
                        'market/{market_id}',
                        'currencies',
                        'tickers',
                        # 'ticker/{market_string}',            # NOTE: dont implement
                        'ticker_by_id/{market_id}',
                        # 'orderbook/{market_string}',         # NOTE: dont implement
                        'orderbook_by_id/{market_id}',         # NOTE: dont implement
                        'market/{market_id}/ohlcv/{interval}',
                    ],
                },
                'private': {
                    'get': [
                        # 'user/me',                             # NOTE: dont implement
                        'user/balances',
                        'user/market/{market_id}',
                        'user/orders',
                        'user/order/{order_id}',
                        'user/withdraws',
                        'user/withdraw/{withdraw_id}',
                        'user/deposits',
                        # 'user/deposit/{deposit_id}',           # NOTE: This endpoint currently non-functional
                        'user/transfers'                         # NOTE: Returns a list of the user's Transfers and metadata.
                    ],
                    'post': [
                        'user/cancel_order',
                        # 'user/deposit_address/{currency}'       # NOTE: dont implement

                        'user/sell_limit',
                        'user/buy_limit',
                    ],
                },
            },
            # 'commonCurrencies': {
            #     'EPC': 'Epacoin',
            # },
            'fees': {
                'trading': {
                    'maker': 0.005,
                    'taker': 0.005,
                },
            },
            'precision': {
                'amount': 6,
                'price': 8,
            },
        })

    # def fetch_currencies(self, params={}):
    #     currencies = self.publicGetCurrencies(params)
    #     ids = list(currencies.keys())
    #     result = {}
    #     for i in range(0, len(ids)):
    #         id = ids[i]
    #         currency = currencies[id]
    #         precision = self.safe_integer(currency, 'decimal')
    #         uppercase = id.upper()
    #         code = self.common_currency_code(uppercase)
    #         active = self.safe_integer(currency, 'active') == 1
    #         maintenance = self.safe_integer(currency, 'under_maintenance')
    #         if maintenance != 0:
    #             active = False
    #         canWithdraw = self.safe_integer(currency, 'is_withdrawal_active') == 1
    #         canDeposit = self.safe_integer(currency, 'is_deposit_active') == 1
    #         if not canWithdraw or not canDeposit:
    #             active = False
    #         result[code] = {
    #             'id': id,
    #             'code': code,
    #             'name': currency['name'],
    #             'active': active,
    #             'precision': precision,
    #             'funding': {
    #                 'withdraw': {
    #                     'active': canWithdraw,
    #                     'fee': self.safe_float(currency, 'txWithdrawalFee'),
    #                 },
    #                 'deposit': {
    #                     'active': canDeposit,
    #                     'fee': self.safe_float(currency, 'txDepositFee'),
    #                 },
    #             },
    #             'limits': {
    #                 'amount': {
    #                     'min': self.safe_float(currency, 'minAmountTrade'),
    #                     'max': math.pow(10, precision),
    #                 },
    #                 'price': {
    #                     'min': math.pow(10, -precision),
    #                     'max': math.pow(10, precision),
    #                 },
    #                 'cost': {
    #                     'min': None,
    #                     'max': None,
    #                 },
    #                 'withdraw': {
    #                     'min': self.safe_float(currency, 'MinWithdrawal'),
    #                     'max': math.pow(10, precision),
    #                 },
    #                 'deposit': {
    #                     'min': self.safe_float(currency, 'minDeposit'),
    #                     'max': None,
    #                 },
    #             },
    #             'info': currency,
    #         }
    #     return result

    def fetch_markets(self, params={}):
        markets = self.publicGetMarkets()['data']['markets']

        result = []

        for market in markets:
            id = market['id']

            baseId = market['market_currency']
            quoteId = market['base_currency']

            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)

            symbol = base + '/' + quote
            active = market['can_trade']

            precision = self.precision

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
        timestamp = ticker['date']
        ticker = ticker['ticker']
        last = self.safe_float(ticker, 'last')

        open_price = self.safe_float(ticker, 'open')
        if last and open_price:
            change = last - open_price
        else:
            change = None

        if self.safe_float(ticker, 'day_change'):
            percentage = self.safe_float(ticker, 'day_change') * 100
        else:
            percentage = None

        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'day_high'),
            'low': self.safe_float(ticker, 'day_low'),
            'bid': self.safe_float(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'ask'),
            'askVolume': None,
            'vwap': None,
            'open': self.safe_float(ticker, 'day_open'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': change,
            'percentage': percentage,
            'average': self.safe_float(ticker, 'day_avg_price'),
            'baseVolume': self.safe_float(ticker, 'day_volume_market'),
            'quoteVolume': self.safe_float(ticker, 'day_volume_base'),
            'info': ticker,
        }

    def fetch_ticker(self, symbol, params={}):
        self.load_markets()
        market = self.market(symbol)
        ticker = self.publicGetTickerByIdMarketId(self.extend({
            'market_id': market['id'],
        }, params))['data']

        ticker = {
            'date': self.milliseconds(),
            'ticker': ticker,
        }
        return self.parse_ticker(ticker, market)

    def fetch_tickers(self, symbols=None, params={}):
        self.load_markets()
        tickers = self.publicGetTickers(params)['data']['markets']
        result = {}
        timestamp = self.milliseconds()

        for ticker in tickers:
            market = self.markets_by_id[ticker['id']]
            symbol = market['symbol']
            ticker = {
                'date': timestamp,
                'ticker': ticker,
            }
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()

        timestamp = self.milliseconds()

        orderbook = self.publicGetOrderbookByIdMarketId(self.extend({
            'market_id': self.market_id(symbol),
        }, params))['data']

        result = dict()

        buy_orders = list()
        for price, amount in orderbook['buy'].items():
            buy_orders.append([float(price), float(amount)])

        result['buy'] = sorted(buy_orders, key=lambda t: t[0], reverse=True)

        sell_orders = list()
        for price, amount in orderbook['sell'].items():
            sell_orders.append([float(price), float(amount)])

        result['sell'] = sorted(sell_orders, key=lambda t: t[0])

        return self.parse_order_book(result, timestamp, 'buy', 'sell')

    def fetch_balance(self, params={}):
        self.load_markets()
        balances = self.privateGetUserBalances(params)['data']['balances']

        result = {'info': balances}

        for balance in balances:
            amount = balance['balance']
            currency = self.common_currency_code(balance['currency'])
            account = {
                'free': float(amount),
                'used': 0.0,
                'total': float(amount),
            }
            account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def parse_trade(self, trade, market=None):
        # Common fields
        created_at = datetime.strptime(trade['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp = int(created_at.timestamp() * 1000)

        symbol = market['symbol']

        price = self.safe_float(trade, 'price')
        amount = self.safe_float(trade, 'market_amount')

        # Result
        result = dict()

        result['datetime'] = self.iso8601(timestamp)
        result['timestamp'] = timestamp

        result['symbol'] = symbol

        result['price'] = price
        result['amount'] = amount
        result['info'] = trade['info']

        # My trade info
        trade_id = self.safe_string(trade, 'id')
        if trade_id:
            result['id'] = trade_id
            result['order'] = self.safe_string(trade, 'order_id')
            result['type'] = trade['type']
            result['side'] = trade['side']

            if trade['taker']:
                result['takerOrMaker'] = 'taker'
            else:
                result['takerOrMaker'] = 'maker'

            result['cost'] = self.safe_float(trade, 'base_amount')

            fee = self.safe_float(trade, 'base_fee')
            fee_currency = market['quote']

            result['fee'] = {
                'cost': fee,
                'currency': fee_currency
            }

        return result

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        data = self.publicGetMarketMarketId(self.extend({
            'market_id': market['id'],
        }, params))['data']

        trades = list()
        for trade in data['recent_trades']:
            trade_obj = trade.copy()
            trade_obj['info'] = trade

            trades.append(trade_obj)

        return self.parse_trades(trades, market, since, limit)

    def parse_order(self, order, market=None):
        order_id = self.safe_string(order, 'id')

        market = self.markets_by_id[order['market_id']]
        symbol = market['symbol']

        created_at = datetime.strptime(order['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp = int(created_at.timestamp() * 1000)

        side, order_type = order['order_type'].split('_')
        if order['open']:
            status = 'open'
        else:
            status = 'closed'

        price = self.safe_float(order, 'price')
        amount = self.safe_float(order, 'market_amount')
        remaining = self.safe_float(order, 'market_amount_remaining')

        filled = amount - remaining
        cost = filled * price

        trades = list()
        if order['trades']:
            for trade in order['trades']:
                trade_obj = trade.copy()

                trade_obj['order_id'] = order_id
                trade_obj['info'] = trade

                trades.append(self.parse_trade(trade_obj, market=market))

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
            'trades': trades,
            'info': order['info'],
        }

    def create_order(self, symbol, type, side, amount, price=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        if side == 'buy':
            method = 'privatePostUserBuyLimit'
        else:
            method = 'privatePostUserSellLimit'

        data = getattr(self, method)(self.extend({
            'market_id': market['id'],
            'price': str(self.price_to_precision(symbol, price)),
            'amount': str(self.amount_to_precision(symbol, amount)),
        }, params))['data']['order']

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

        result = self.privatePostUserCancelOrder(self.extend({
            'id': int(id)
        }, params))

        return result

    def fetch_order(self, id, symbol=None, params={}):
        self.load_markets()

        data = self.privateGetUserOrderOrderId(self.extend({
            'order_id': id
        }, params))['data']['order']

        order_obj = data.copy()
        order_obj['info'] = data

        order = self.parse_order(order_obj)

        return order

    def _parse_raw_orders(self, raw_orders, market, since, limit):
        order_objes = list()

        for order in raw_orders:
            order_obj = order.copy()
            order_obj['info'] = order

            order_objes.append(order_obj)

        return self.parse_orders(order_objes, market, since, limit)

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()

        if symbol:
            market = self.market(symbol)
            data = self.privateGetUserMarketMarketId(self.extend({
                'market_id': int(market['id'])
            }, params))['data']
            raw_orders = data['closed_orders'] + data['open_orders']
        else:
            market = None
            raw_orders = self.privateGetUserOrders(self.extend({}, params))['data']['orders']

        return self._parse_raw_orders(raw_orders, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        if symbol:
            market = self.market(symbol)
            data = self.privateGetUserMarketMarketId(self.extend({
                'market_id': market['id']
            }, params))['data']
            raw_orders = data['open_orders']

            orders = self._parse_raw_orders(raw_orders, market, since, limit)
        else:
            total_orders = self.fetch_orders(symbol, since, limit, params)
            orders = self.filter_by(total_orders, 'status', 'open')

        return orders

    def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        if symbol:
            market = self.market(symbol)
            data = self.privateGetUserMarketMarketId(self.extend({
                'market_id': market['id']
            }, params))['data']
            raw_orders = data['closed_orders']

            orders = self._parse_raw_orders(raw_orders, market, since, limit)
        else:
            total_orders = self.fetch_orders(symbol, since, limit, params)
            orders = self.filter_by(total_orders, 'status', 'closed')

        return orders

    # def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
    #     self.load_markets()
    #     market = self.market(symbol)
    #     trades = self.privatePostTradeHistory(self.extend({
    #         'market': market['id'],
    #     }, params))
    #     return self.parse_trades(trades['trade_history'], market, since, limit)

    # def fetch_deposit_address(self, code, params={}):
    #     self.load_markets()
    #     currency = self.currency(code)
    #     response = self.privatePostDepositAddress(self.extend({
    #         'currency': currency['id'],
    #     }, params))
    #     address = self.safe_string(response, 'deposit_address')
    #     self.check_address(address)
    #     tag = self.safe_string(response, 'payment_id')
    #     return {
    #         'currency': code,
    #         'address': address,
    #         'tag': tag,
    #         'info': response,
    #     }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api']
        query = self.omit(params, self.extract_params(path))

        url += '/' + self.implode_params(path, params)

        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()

            if method == 'GET':
                if query:
                    url += '?' + self.urlencode(query)
            elif query:
                body = self.json(query)

            timestamp = str(int(time.time()))

            request_details = method + "\n"
            request_details += '/v1/' + self.implode_params(path, params) + "\n"
            request_details += timestamp + "\n"

            if body:
                request_details += body + "\n"
            else:
                request_details += "\n"

            request_details += self.secret

            hsh = hashlib.sha256(request_details.encode("utf8")).digest()
            signature = base64.b64encode(hsh)

            headers = {
                "Authorization": "HMAC-SHA256 {}:{}".format(self.apiKey, signature.decode("utf8")),
                "HMAC-Timestamp": timestamp,
            }

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
