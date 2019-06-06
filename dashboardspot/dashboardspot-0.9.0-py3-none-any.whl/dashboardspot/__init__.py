import time
import json
import requests

__version__ = '0.9.0'

class DashboardSpot(object):
    """DashboardSpot master class."""

    def __init__(self, api_key):
        self.api_key = api_key

    def hit(self, label, **kwargs):
        payload = kwargs
        payload['label'] = label
        if not 'timestamp' in payload:
            payload['timestamp'] = int(time.time())
        payload['api_key'] = self.api_key
        respone = requests.post('https://8drniy1zb7.execute-api.us-east-1.amazonaws.com/dev/webhook', data=json.dumps(payload))
        print(respone.text)
        return True
