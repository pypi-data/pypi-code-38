"""
MSG91 Client
"""
import requests

from urllib.parse import quote

class Client(object):
    """ A client for accessing the MSG91 API. """
    API_ENDPOINT = "http://api.msg91.com"

    TRANSACTIONAL_URL = "/api/v2/sendsms"
    TRANSACTIONAL_ROUTE = "4"

    def __init__(self, authkey):
        """
        Initializes the MSG91 Client
        :param str authkey: Authkey to authenticate with
        :param dict environment: Environment to look for auth details, defaults to os.environ
        :returns: MSG91 Client
        :rtype: herald.clients.msg91.Client
        """
        self.authkey = authkey

    def __repr__(self):
        """
        Provide a friendly representation
        :returns: Machine friendly representation
        :rtype: str
        """
        return '<MSG91 {}>'.format(self.authkey)


    def send_transactional(self, sender_id, to_number, message):
        """
        Send transactional SMS
        """
        url = self.API_ENDPOINT + self.TRANSACTIONAL_URL


        headers = {
            'authkey': self.authkey,
            'content-type': "application/json"
        }

        if len(to_number) < 10:
            raise Exception(
                "Invalid mobile number. You have entered less than 10 digits in the mobile number."
            )

        message = quote(message)

        res = requests.post(url, json={
            'sender': sender_id,
            'route': self.TRANSACTIONAL_ROUTE,
            'sms': [{
                'message': message,
                'to': [to_number]
            }]
        }, headers=headers)

        return res
