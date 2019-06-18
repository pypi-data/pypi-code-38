''' Authentication key to use Crackle api's '''
from hashlib import sha1
# pylint: disable=too-few-public-methods
import hmac
import datetime


class Authentication(object):
    ''' Call get_hmac_sha1 to get the authorization key
        auth.__init__('website', '/Service.svc/register/config'
    '''

    def __init__(self, configuration, endpoint=''):
        self.configuration = configuration
        self.endpoint = endpoint
        self.key = self.get_hmac_sha1(self.endpoint)

    def get_hmac_sha1(self, endpoint):
        ''' Gets the hmac sha1 authentication key '''
        host = self.configuration.host
        partner_id = self.configuration.partner_id
        secret = self.configuration.secret

        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M')
        msg_str = host + endpoint + '|' + timestamp
        message = msg_str.encode('utf-8')
        key = secret.encode('utf-8')

        hashed = hmac.new(key, message, sha1).hexdigest()
        return hashed.upper() + '|' + timestamp + '|' + partner_id + '|1'
