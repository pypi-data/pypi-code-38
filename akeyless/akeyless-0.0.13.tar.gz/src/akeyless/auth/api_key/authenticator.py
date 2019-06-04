import base64
import time

import ecdsa
from ecdsa.util import sigencode_der
from hashlib import sha256

from akeyless.api.base import AkeylessApiI
from akeyless.auth.base import Authenticator
from akeyless.crypto.random import token_hex
from akeyless.exceptions import CredsRenewalError


class ApiKeyAuthenticator(Authenticator):

    def __init__(self, akeyless_api, policy_id, base64_prv_key):
        # type: (AkeylessApiI, str, str) -> None
        super(ApiKeyAuthenticator, self).__init__(akeyless_api)
        self.policy_id = policy_id
        self.prv_key = ecdsa.SigningKey.from_string(base64.b64decode(base64_prv_key), curve=ecdsa.NIST256p,
                                                    hashfunc=sha256)

    def authenticate(self):
        # type: () -> str
        try:
            timestamp, nonce, signature = self._create_api_signature()
            return self.akeyless_api.authenticate_uam_api_key_policy(self.policy_id, timestamp, nonce, signature)
        except Exception as e:
            raise CredsRenewalError(e)

    def _create_api_signature(self):
        # type: () -> (int, str, str)
        nonce = self.__generate_nonce()
        timestamp = int(time.time())
        signature = base64.b64encode(self.prv_key.sign(data=self._string_to_sign(nonce, timestamp),
                                                       hashfunc=sha256, sigencode=sigencode_der))
        return timestamp, nonce, signature

    def _string_to_sign(self, nonce, time_sig):
        # type: (str, int) -> bytes
        return str.encode("signatureForTemporaryCredential;policy_id=" +
                          self.policy_id + ";nonce=" + nonce + ";time=" + str(time_sig))

    @staticmethod
    def __generate_nonce():
        return token_hex(8)
