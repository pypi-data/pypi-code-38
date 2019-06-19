from __future__ import print_function
import pendulum
import requests
import furl
import os.path
import json

from .constant import BASE_API_URL, JSON_SETTINGS


class Private:

    def __init__(self, options, url=None):
        self.url = url if url is not None else BASE_API_URL
        self.options = options
        self.current_token = None

    def profile_info(self):
        """ https://apidocs.stex.com/#/Profile/get_profile_info """
        return self.send_request(self.url + '/profile/info')

    def profile_wallets(self, sort='DESC', sort_by='BALANCE'):
        """ https://apidocs.stex.com/#/Profile/get_profile_wallets """
        params = {
            'sort': sort,
            'sortBy': sort_by
        }
        f = furl.furl(self.url + '/profile/wallets').add(params)
        return self.send_request(f.url)

    def profile_wallets_by_id(self, wallet_id):
        """ See https://apidocs.stex.com/#/Profile/get_profile_wallets__walletId_ """
        return self.send_request(self.url + '/profile/wallets/' + str(wallet_id))

    def post_profile_wallets_by_currency_id(self, currency_id):
        """ See https://apidocs.stex.com/#/Profile/post_profile_wallets__currencyId_ """
        return self.send_request(self.url + '/profile/wallets/' + str(currency_id), 'POST')

    def profile_deposit_address_by_wallet_id(self, wallet_id):
        """ See https://apidocs.stex.com/#/Profile/get_profile_wallets_address__walletId_ """
        return self.send_request(self.url + '/profile/wallets/address/' + str(wallet_id))

    def new_deposit_address_by_wallet_id(self, wallet_id):
        """ See https://apidocs.stex.com/#/Profile/post_profile_wallets_address__walletId_ """
        return self.send_request(self.url + '/profile/wallets/address/' + str(wallet_id), 'POST')

    def profile_deposits(self, params=None):
        """ See https://apidocs.stex.com/#/Profile/get_profile_deposits """
        if params is None:
            params = {}
        f = furl.furl(self.url + '/profile/deposits').add(params)
        return self.send_request(f.url)

    def profile_deposits_by_id(self, deposit_id):
        """ See https://apidocs.stex.com/#/Profile/get_profile_deposits__id_ """
        return self.send_request(self.url + '/profile/deposits/' + str(deposit_id))

    def profile_withdrawals(self, params=None):
        """ See https://apidocs.stex.com/#/Profile/get_profile_withdrawals """
        if params is None:
            params = {}
        f = furl.furl(self.url + '/profile/withdrawals').add(params)
        return self.send_request(f.url)

    def profile_withdrawals_id(self, withdrawal_id):
        """ See https://apidocs.stex.com/#/Profile/get_profile_withdrawals__id_ """
        return self.send_request(self.url + '/profile/withdrawals/' + str(withdrawal_id))

    def create_withdrawal(self, currency_id, amount, address, additional_address=None):
        """ See https://apidocs.stex.com/#/Profile/post_profile_withdraw """
        data = {
            'currency_id': currency_id,
            'amount': amount,
            'address': address,
        }
        if additional_address is not None:
            data['additional_address_parameter'] = additional_address
        return self.send_request(self.url + '/profile/withdraw', 'POST', 'form', data)

    def cancel_withdrawal(self, withdrawal_id):
        """ See https://apidocs.stex.com/#/Profile/delete_profile_withdraw__withdrawalId_ """
        return self.send_request(self.url + '/profile/withdraw/' + str(withdrawal_id), 'DELETE')

    def reports_orders(self, params=None):
        """ See https://apidocs.stex.com/#/Trading%20History/get_reports_orders """
        if params is None:
            params = {}
        f = furl.furl(self.url + '/reports/orders').add(params)
        return self.send_request(f.url)

    def reports_orders_id(self, order_id):
        """ See https://apidocs.stex.com/#/Trading%20History/get_reports_orders__orderId_ """
        return self.send_request(self.url + '/reports/orders/' + str(order_id))

    def trading_fees_by_pair_id(self, currency_pair_id):
        """ See https://apidocs.stex.com/#/Trading/get_trading_fees__currencyPairId_ """
        return self.send_request(self.url + '/trading/fees/' + str(currency_pair_id))

    def trading_open_orders(self):
        """ See https://apidocs.stex.com/#/Trading/get_trading_orders """
        return self.send_request(self.url + '/trading/orders')

    def trading_cancel_all_open_orders(self):
        """ See https://apidocs.stex.com/#/Trading/delete_trading_orders """
        return self.send_request(self.url + '/trading/orders', 'DELETE')

    def trading_orders_by_pair_id(self, currency_pair_id):
        """ See https://apidocs.stex.com/#/Trading/get_trading_orders__currencyPairId_ """
        return self.send_request(self.url + '/trading/orders/' + str(currency_pair_id))

    def cancel_trading_orders_by_pair_id(self, currency_pair_id):
        """ See https://apidocs.stex.com/#/Trading/delete_trading_orders__currencyPairId_ """
        return self.send_request(self.url + '/trading/orders/' + str(currency_pair_id), 'DELETE')

    def create_trading_orders_by_pair_id(self, currency_pair_id, type, amount, price, trigger_price=None):
        """ See https://apidocs.stex.com/#/Trading/post_trading_orders__currencyPairId_ """
        data = {
            'type': type,
            'amount': amount,
            'price': price,
        }
        if trigger_price is not None:
            data['trigger_price'] = trigger_price
        return self.send_request(self.url + '/trading/orders/' + str(currency_pair_id), 'POST', 'form', data)

    def get_trading_orders_by_id(self, order_id):
        """ See https://apidocs.stex.com/#/Trading/get_trading_order__orderId_ """
        return self.send_request(self.url + '/trading/order/' + str(order_id))

    def cancel_trading_orders_by_id(self, order_id):
        """ See https://apidocs.stex.com/#/Trading/delete_trading_order__orderId_ """
        return self.send_request(self.url + '/trading/order/' + str(order_id), 'DELETE')

    def send_request(self, url, method='GET', format_type='url', form=None):
        headers = {'Content-Type': 'application/json', 'User-Agent': 'stex_python_client'}
        try:
            headers['Authorization'] = 'Bearer {}'.format(self.get_token())
            if method == 'GET' and format_type == 'url':
                r = requests.get(url, headers=headers)
                return r.json()
            if method == 'POST' and format_type == 'url':
                r = requests.post(url, headers=headers)
                return r.json()
            if method == 'DELETE' and format_type == 'url':
                r = requests.delete(url, headers=headers)
                return r.json()
            if format_type == 'form' and method == 'POST':
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                r = requests.post(url, headers=headers, data=form)
                return r.json()
        except Exception as e:
            return e

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
