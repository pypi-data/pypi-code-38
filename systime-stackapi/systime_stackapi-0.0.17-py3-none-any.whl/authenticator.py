import requests
from collections import OrderedDict
import time
import hmac
import json
import jwt


class Authenticator(object):
    def __init__(self, client_key_id, shared_secret, **kwargs):
        self.client_key_id = client_key_id
        self.shared_secret = shared_secret
        self.requested_token_lifetime = kwargs.get('requested_token_lifetime', 1800)
        self.auth_endpoint = kwargs.get('auth_endpoint', 'https://auth.api.systime.dk/auth')
        self.algorithm = kwargs.get('algorithm', 'sha3_512')
        self.existing_token = None

    def retrieve_new_service_bearer_token(self, service_key_id):
        json_payload = self.build_payload(service_key_id)
        token = self.authenticate(json_payload)
        return token

    def format_bearer_token_for_header(self, token):
        formatted_token = 'Bearer %s' % (token)
        return formatted_token

    def get_service_bearer_token(self, service_key_id):
        if self.existing_token is not None and self.validate_token_expiry(self.existing_token, 300):
            return self.format_bearer_token_for_header(self.existing_token)

        self.existing_token = self.retrieve_new_service_bearer_token(service_key_id)
        return self.format_bearer_token_for_header(self.existing_token)

    def validate_token_expiry(self, token, required_expiry_left):
            decoded_token = jwt.decode(token, verify=False)
            if decoded_token['exp'] < time.time() + required_expiry_left:
                return False
            return True

    def build_payload(self, service_key_id):
        d = OrderedDict()
        d['clientKeyId'] = self.client_key_id
        d['serviceKeyId'] = service_key_id
        d['time'] = int(time.time())
        d['expiry'] = self.requested_token_lifetime

        hmac_components = ''
        for value in d.values():
            hmac_components += str(value)

        signature = hmac.new(self.shared_secret.encode('utf-8'), hmac_components.encode('utf-8'), self.algorithm)
        hex_signature = signature.hexdigest()
        d['signature'] = hex_signature
        return json.dumps(d)

    def authenticate(self, json_payload):
        r = requests.post(self.auth_endpoint, data=json_payload, headers={'Content-Type': 'application/json'})

        if r.status_code == 200:
            json_token = json.loads(r.text)
            token = json_token['JWTToken']
            return token
        else:
            raise Exception('Authentication failed')

