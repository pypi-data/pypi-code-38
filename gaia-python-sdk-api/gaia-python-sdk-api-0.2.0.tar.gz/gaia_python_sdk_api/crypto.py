import base64
import hashlib
import hmac

"""
This class is used to encrypt the data before sending it to G.A.I.A.
"""
class HMAC:

    def __init__(self, secret):
        self.secret = secret

    """
    Hashes the given string data.
    """
    def hash(self, data):
        key = self.secret.encode("UTF-8")
        msg = data.encode("UTF-8")

        dig = hmac.new(key, msg=msg, digestmod=hashlib.sha256).digest()
        return base64.b64encode(dig).decode()
