import requests

from api.client_options import ClientOptions
from api.transporter.abstract_transporter import ITransporter

"""
ITransporter implementatin which is based on the HTTP protocol.
"""
class HttpTransport(ITransporter):

    def __init__(self, url, options: ClientOptions):
        self.url = url
        self.options = options

    def transport(self, payload):
        headers = {
            "Content-Type": "application/json",
            "X-GAIA-APIKEY": self.options.apikey,
            "X-GAIA-SIGNATURE": self.options.secret
        }
        response = requests.post(self.url, json=payload, headers=headers)
        return response.json()
