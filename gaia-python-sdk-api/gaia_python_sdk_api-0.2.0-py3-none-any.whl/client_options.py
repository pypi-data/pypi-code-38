"""
This class stores the apiKey/secret tuple used by the transporter implementation
to establish a connection to G.A.I.A.
"""
class ClientOptions:

    def __init__(self, apikey, secret):
        self.apikey = apikey
        self.secret = secret
