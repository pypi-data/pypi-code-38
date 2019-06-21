import socketio
import pendulum
import requests
import os.path
import json
from .constant import JSON_SETTINGS, SOCKET_URL


class WebsocketStex:

    def __init__(self, options=None, debug=False, url=None):
        """ See https://docs.google.com/document/d/1CaD7qV6UzSJ72DMY0qLHnRgabhadVV0Kxc2_lhEFWKA """
        self.url = url if url is not None else SOCKET_URL
        self.options = options
        self.current_token = None

        self.client = socketio.Client(logger=debug)
        self.client.connect(self.url, transports=['websocket'])

        self.client.on('connect', self.on_connect)
        self.client.on('disconnect', self.on_disconnect)
        self.client.on('reconnect', self.on_reconnect)
        self.client.on('subscription_error', self.on_subscription_error)

    def subscribe_rate(self, callback):
        channel = 'rate'
        self.client.on("App\\Events\\Ticker", callback)
        self.subscribe(channel)

    def subscribe_order_fill_created(self, currency_pair_id, callback):
        channel = 'trade_c' + str(currency_pair_id)
        self.client.on("App\\Events\\OrderFillCreated", callback)
        self.subscribe(channel)

    def subscribe_glass_total_changed(self, currency_pair_id, type, callback):
        channel = type + '_total_data' + str(currency_pair_id)
        self.client.on("App\\Events\\GlassTotalChanged", callback)
        self.subscribe(channel)

    def subscribe_glass_row_changed(self, currency_pair_id, type, callback):
        channel = type + '_data' + str(currency_pair_id)
        self.client.on("App\\Events\\GlassRowChanged", callback)
        self.subscribe(channel)

    def subscribe_best_price_changed(self, currency_pair_id, type, callback):
        channel = 'best_' + type + '_price_' + str(currency_pair_id)
        self.client.on("App\\Events\\BestPriceChanged", callback)
        self.subscribe(channel)

    def subscribe_candle_changed(self, currency_pair_id, chart_type, callback):
        channel = 'stats_data_' + str(chart_type) + '_' + str(currency_pair_id)
        self.client.on("App\\Events\\CandleChanged", callback)
        self.subscribe(channel)

    def subscribe_balance_changed(self, wallet_id, callback):
        channel = 'private-balance_changed_w_' + str(wallet_id)
        self.client.on("App\\Events\\BalanceChanged", callback)
        self.subscribe_private(channel)

    def subscribe_user_order(self, type, user_id, currency_pair_id, callback):
        channel = 'private-' + str(type) + '_user_data_u' + str(user_id) + 'c' + str(currency_pair_id)
        self.client.on("App\\Events\\UserOrder", callback)
        self.subscribe_private(channel)

    def subscribe_user_order_deleted(self, user_id, currency_pair_id, callback):
        channel = 'private-del_order_u-' + str(user_id) + 'c' + str(currency_pair_id)
        self.client.on("App\\Events\\UserOrderDeleted", callback)
        self.subscribe_private(channel)

    def subscribe_user_order_fill(self, user_id, currency_pair_id, callback):
        channel = 'private-trade_u' + str(user_id) + 'c' + str(currency_pair_id)
        self.client.on("App\\Events\\UserOrderFillCreated", callback)
        self.subscribe_private(channel)

    def subscribe(self, name):
        self.client.emit('subscribe', {
            'channel': name,
            'auth': {}
        })

    def subscribe_private(self, name):
        auth = {'headers': {'Authorization': 'Bearer ' + self.get_token()}}
        self.client.emit('subscribe', data={
            'channel': name,
            'auth': auth
        })

    def get_token(self):
        try:
            if os.path.isfile(JSON_SETTINGS):
                with open(JSON_SETTINGS) as json_file:
                    self.current_token = json.load(json_file)
            else:
                self.current_token = {
                    "access_token": self.options['tokenObject']['access_token'],
                    "refresh_token": self.options['tokenObject']['refresh_token'],
                    "expires_in": None,
                    "expires_in_date": None
                }
            if self.current_token['expires_in_date'] is not None:
                if pendulum.parse(self.current_token['expires_in_date']) > pendulum.now('UTC'):
                    return self.current_token['access_token']

            session = requests.Session()
            r = session.post(self.options['accessTokenUrl'], data={
                'grant_type': 'refresh_token',
                'refresh_token': self.options['tokenObject']['refresh_token'],
                'client_id': self.options['client']['id'],
                'client_secret': self.options['client']['secret'],
                'scope': self.options['scope'],
            })
            if r.status_code != 200:
                if os.path.isfile(JSON_SETTINGS):
                    os.remove(JSON_SETTINGS)
                raise requests.HTTPError(r.text)
            self.current_token = r.json()
            self.current_token['expires_in_date'] = pendulum.now('UTC').add(
                seconds=self.current_token['expires_in']).to_datetime_string()
            with open(JSON_SETTINGS, 'w', encoding='utf-8') as outfile:
                json.dump(self.current_token, outfile, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(e)
        return self.current_token['access_token']

    @staticmethod
    def on_connect():
        print('Connected')

    @staticmethod
    def on_disconnect():
        print('Disconnected')

    @staticmethod
    def on_reconnect():
        print('Reconnect')

    @staticmethod
    def on_subscription_error(*args):
        print('Error', args)
