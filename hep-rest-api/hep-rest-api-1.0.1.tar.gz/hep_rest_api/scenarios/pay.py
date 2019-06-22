"""The implementation of HEP Payment protocol

"""

__copyright__ = """ Copyright (c) 2019 Newton Foundation. All rights reserved."""
__version__ = '1.0'
__author__ = 'xiawu@zeuux.org'

import datetime
import logging
from hep_rest_api.scenarios import BaseHelper
from hep_rest_api import models

logger = logging.getLogger(__name__)


class PayHelper(BaseHelper):
    def generate_pay_request(self,
                             order_number,
                             price_currency,
                             total_price,
                             description,
                             seller,
                             customer,
                             broker='',
                             expired=300,
                             uuid=None):
        """Generate the payment request
        
        :param str dapp_id: The DApp ID
        :param str order_number: The order number
        :param str price_currency: The symbol of fiat or digital token, such as USD, CNY, NEW,BTC,ETH.
        :param str total_price: The amount of fiat or digital token, unit is the minimum unit of given fiat or digital token.
        :param str description: The order description
        :param str seller: The seller's NewID
        :param str customer: The customer's NewID
        :param str broker: The broker's NewID. optional.
        :param int expired: The expired time of request
        :param str uuid: The request uuid for desktop-browser. optional.
        :rtype: dict
        :return: The request information including signature
        """
        if not uuid:
            raise AttributeError(
                "uuid can not be None"
            )
        if not order_number:
            raise AttributeError(
                "order number can not be None"
            )
        data = {
            'action': self.action_auth_pay,
            'order_number': order_number,
            'expired': int(datetime.datetime.now().timestamp()) + expired,
            'price_currency': price_currency,
            'total_price': total_price,
            'description': description,
            'seller': seller,
            'customer': customer,
            'broker': broker,
            'uuid': uuid,
            'dapp_id': self.dapp_id
        }
        sign_data = self.generate_sign_data(data)
        hmac_data = self.sign_hmac(sign_data)
        final_data = self.sign_secp256r1(hmac_data)
        # start request
        auth_cache = models.PayCacheRequest(**final_data)
        auth_response = self.api_client.rest_newnet_caches_pay_create(auth_cache, self.api_version)
        return auth_response

    def generate_qrcode_string(self, pay_hash):
        """Generate the hep-based scheme string string for QRCode 
        
        :param str pay_hash: The pay request hash
        :rtype: str
        :return: The QRcode string
        """
        protocol = self.base_parameters.get('protocol')
        action = self.action_auth_pay
        qrcode_str = "%s://%s/?action=%s&pay_hash=%s" % (protocol.lower(), self.dapp_id, action, pay_hash)
        return qrcode_str

    def validate_pay_callback(self, data):
        """Validate the response of pay callback sent by end users such as NewPay users 
        
        :param dict data: The callback data
        :rtype: bool
        :return: True if valid data, otherwise False
        """
        return self.validate_r1_data(data)

    def get_confirmed_transaction(self, transaction_id):
        """ Validate transaction by transaction id. and you can get the order_number, block height and etc.

        :param transaction_id: txid
        :rtype: dict
        :return: dict about transaction
        """
        params = {}
        sign_data = self.generate_sign_data(params)
        hmac_data = self.sign_hmac(sign_data)
        hmac_data['txid'] = transaction_id
        hmac_data['api_version'] = self.api_version
        response = self.api_client.rest_newchain_tx_read(**hmac_data)
        return response



