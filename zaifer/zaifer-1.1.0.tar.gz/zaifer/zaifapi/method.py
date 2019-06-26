from zaifer.zaifapi.connection import *


class Chart():
    '''
    チャート情報を取得します。
    '''

    def __init__(self, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(url_config.chartApiUrl)

    def get_ohlc(self, currency_pair: str, period: str, since: datetime, end: datetime) -> dict:
        '''
        チャート情報を取得します。
        period :
            1分足:1、5分足:5、15分足:15、30分足:30、1時間足:60、4時間足:240、8時間足:480
            日足:D、週足:?、月足:?
        '''
        params = {
            'symbol': currency_pair,
            'resolution': period,
            'from': str(int(time.mktime(since.timetuple()))),
            'to': str(int(time.mktime(end.timetuple())))
        }
        return self._connection.get('/history', params)


class Account():
    '''
    アカウント情報を取得します。
    '''

    def __init__(self, key, secret, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(url_config.tradeApiUrl, key, secret)

    def get_info(self) -> dict:
        '''
        アカウント情報を取得します。
        '''
        params = {
            'method': 'get_info',
            'nonce': NonceGenerator.generate()
        }
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_info2(self) -> dict:
        '''
        アカウント情報を取得します。(軽量版)
        '''
        params = {
            'method': 'get_info2',
            'nonce': NonceGenerator.generate()
        }
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_personal_info(self) -> dict:
        '''
        アカウントのチャット情報を取得します。
        '''
        params = {
            'method': 'get_personal_info',
            'nonce': NonceGenerator.generate()
        }
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_id_info(self) -> dict:
        '''
        アカウントの基本情報を取得します。
        '''
        params = {
            'method': 'get_id_info',
            'nonce': NonceGenerator.generate()
        }
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def withdraw(self, currency: str, address: str, amount: Decimal, message: str = None, opt_fee: Decimal = None) -> dict:
        '''
        出金依頼を送信します。
        '''
        params = {
            'method': 'withdraw',
            'nonce': NonceGenerator.generate(),
            'currency': currency,
            'address': address,
            'amount': amount
        }
        if message is not None:
            params['message'] = message
        if opt_fee is not None:
            params['opt_fee'] = opt_fee
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_deposit_history_by_period(self, currency: str, since: datetime = None, end: datetime = None) -> dict:
        '''
        入金履歴を取得します。
        '''
        params = {
            'method': 'deposit_history',
            'nonce': NonceGenerator.generate(),
            'currency': currency
        }
        if since is not None:
            params['since'] = str(int(time.mktime(since.timetuple())))
        if end is not None:
            params['end'] = str(int(time.mktime(end.timetuple())))
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_withdraw_history_by_period(self, currency: str, since: datetime = None, end: datetime = None) -> dict:
        '''
        出金履歴を取得します。
        '''
        params = {
            'method': 'withdraw_history',
            'nonce': NonceGenerator.generate(),
            'currency': currency
        }
        if since is not None:
            params['since'] = str(int(time.mktime(since.timetuple())))
        if end is not None:
            params['end'] = str(int(time.mktime(end.timetuple())))
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)


class Market():
    '''
    現物取引のマーケット情報を取得します。
    '''

    def __init__(self, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(url_config.publicApiUrl)

    def get_currencies(self, currency: str) -> dict:
        '''
        通貨情報を取得します。
        '''
        return self._connection.get('/currencies/{}'.format(currency), None)

    def get_currency_pairs(self, currency_pair: str) -> dict:
        '''
        通貨ペア情報を取得します。
        '''
        return self._connection.get('/currency_pairs/{}'.format(currency_pair), None)

    def get_last_price(self, currency_pair: str) -> dict:
        '''
        現在の終値を取得します。
        '''
        return self._connection.get('/last_price/{}'.format(currency_pair), None)

    def get_ticker(self, currency_pair: str) -> dict:
        '''
        ティッカーを取得します。
        '''
        return self._connection.get('/ticker/{}'.format(currency_pair), None)

    def get_trade_history(self, currency_pair: str) -> dict:
        '''
        全ユーザーの取引履歴を取得します。
        '''
        return self._connection.get('/trades/{}'.format(currency_pair), None)

    def get_depth(self, currency_pair: str) -> dict:
        '''
        板情報を取得します。
        '''
        return self._connection.get('/depth/{}'.format(currency_pair), None)


class Trade():
    '''
    現物取引の注文情報を取得・送信します。
    '''

    def __init__(self, key, secret, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(url_config.tradeApiUrl, key, secret)

    def get_trade_history_by_period(self, currency_pair: str = None, since: datetime = None, end: datetime = None) -> dict:
        '''
        ユーザー自身の取引履歴を取得します。
        '''
        params = {
            'method': 'trade_history',
            'nonce': NonceGenerator.generate()
        }
        if currency_pair is not None:
            params['currency_pair'] = currency_pair
        if since is not None:
            params['since'] = str(int(time.mktime(since.timetuple())))
        if end is not None:
            params['end'] = str(int(time.mktime(end.timetuple())))
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_active_orders(self, currency_pair: str = None) -> dict:
        '''
        現在有効な注文一覧を取得します（未約定注文一覧）。
        '''
        params = {
            'method': 'active_orders',
            'nonce': NonceGenerator.generate()
        }
        if currency_pair is not None:
            params['currency_pair'] = currency_pair
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def open_order(self, currency_pair: str, action: str, price: Decimal, amount: Decimal, limit: Decimal = None, comment: str = None) -> dict:
        '''
        新規注文を送信します。
        '''
        params = {
            'method': 'trade',
            'nonce': NonceGenerator.generate(),
            'currency_pair': currency_pair,
            'action': action,
            'price': price,
            'amount': amount
        }
        if limit is not None:
            params['limit'] = limit
        if comment is not None:
            params['comment'] = comment
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def cancel_order(self, order_id: int) -> dict:
        '''
        キャンセル注文を送信します。
        '''
        params = {
            'method': 'cancel_order',
            'nonce': NonceGenerator.generate(),
            'order_id': order_id
        }
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)


class FutureMarket():
    '''
    先物取引のマーケット情報を取得します。
    '''

    def __init__(self, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(url_config.futureTradeApiUrl)

    def get_groups(self, group_id: int) -> dict:
        '''
        先物取引のグループIDを取得します。
        'all'を指定した場合、取引が終了したものを含むすべてのグループIDを取得し、
        'active'を指定した場合、現在取引可能なグループIDのみを取得します。
        '''
        return self._connection.get('/groups/{}'.format(str(group_id)), None)

    def get_last_price(self, group_id: int, currency_pair: str) -> dict:
        '''
        現在の終値を取得します。
        '''
        return self._connection.get('/last_price/{}/{}'.format(str(group_id), currency_pair), None)

    def get_ticker(self, group_id: int, currency_pair: str) -> dict:
        '''
        ティッカーを取得します。
        '''
        return self._connection.get('/ticker/{}/{}'.format(str(group_id), currency_pair), None)

    def get_trade_history(self, group_id: int, currency_pair: str) -> dict:
        '''
        全ユーザの取引履歴を取得します。
        '''
        return self._connection.get('/trades/{}/{}'.format(str(group_id), currency_pair), None)

    def get_depth(self, group_id: int, currency_pair: str) -> dict:
        '''
        板情報を取得します。
        '''
        return self._connection.get('/depth/{}/{}'.format(str(group_id), currency_pair), None)

    def get_swap_history(self, group_id: int, currency_pair: str) -> dict:
        '''
        確定したスワップポイントの履歴を取得します。
        '''
        return self._connection.get('/swap_history/{}/{}'.format(str(group_id), currency_pair), None)


class MarginTrade():
    '''
    証拠金取引(信用取引および先物取引)の注文情報を取得・送信します。
    '''

    def __init__(self, key, secret, url_config: UrlConfigs = UrlConfigs()):
        '''
        コンストラクタ
        '''
        self._connection = HttpConnection(
            url_config.marginTradeApiUrl, key, secret)

    def get_positions(self, type: str, group_id: int = None, currency_pair: str = None, since: datetime = None, end: datetime = None) -> dict:
        '''
        証拠金取引のユーザー自身の取引履歴を取得します。
        '''
        params = {
            'method': 'get_positions',
            'nonce': NonceGenerator.generate(),
            'type': type
        }
        if group_id is not None:
            params['group_id'] = group_id
        if currency_pair is not None:
            params['currency_pair'] = currency_pair
        if since is not None:
            params['since'] = str(int(time.mktime(since.timetuple())))
        if end is not None:
            params['end'] = str(int(time.mktime(end.timetuple())))
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def position_history(self, type: str, group_id: int, order_id: int) -> dict:
        '''
        証拠金取引のユーザー自身の取引履歴の明細を取得します。
        '''
        params = {
            'method': 'position_history',
            'nonce': NonceGenerator.generate(),
            'type': type,
            'leverage_id': order_id
        }
        if group_id is not None:
            params['group_id'] = group_id
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def get_active_positions(self, type: str, group_id: int = None, currency_pair: str = None) -> dict:
        '''
        証拠金取引の現在有効な注文一覧を取得します（未約定注文一覧）。
        '''
        params = {
            'method': 'active_positions',
            'nonce': NonceGenerator.generate(),
            'type': type
        }
        if group_id is not None:
            params['group_id'] = group_id
        if currency_pair is not None:
            params['currency_pair'] = currency_pair
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def create_position(self, type: str, group_id: int, currency_pair: str, action: str, price: Decimal, amount: Decimal, leverage: Decimal, limit: Decimal = None, stop: Decimal = None) -> dict:
        '''
        証拠金取引の新規注文を送信します。
        '''
        params = {
            'method': 'create_position',
            'nonce': NonceGenerator.generate(),
            'type': type,
            'currency_pair': currency_pair,
            'action': action,
            'price': price,
            'amount': amount,
            'leverage': leverage
        }
        if group_id is not None:
            params['group_id'] = group_id
        if limit is not None:
            params['limit'] = limit
        if stop is not None:
            params['stop'] = stop
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def update_position(self, type: str, group_id: int, order_id: int, price: Decimal, limit: Decimal = None, stop: Decimal = None) -> dict:
        '''
        証拠金取引の修正注文を送信します。
        '''
        params = {
            'method': 'change_position',
            'nonce': NonceGenerator.generate(),
            'type': type,
            'leverage_id': order_id,
            'price': price,
        }
        if group_id is not None:
            params['group_id'] = group_id
        if limit is not None:
            params['limit'] = limit
        if stop is not None:
            params['stop'] = stop
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)

    def cancel_position(self, type: str, group_id: int, order_id: int) -> dict:
        '''
        証拠金取引のキャンセル注文を送信します。
        '''
        params = {
            'method': 'cancel_position',
            'nonce': NonceGenerator.generate(),
            'type': type,
            'leverage_id': order_id
        }
        if group_id is not None:
            params['group_id'] = group_id
        res = self._connection.post(None, params)
        return ResponseParser.parse(res)
