import time
import json
import requests

__version__ = '0.9.1'

class DashboardSpot(object):
    """DashboardSpot master class."""

    def __init__(self, api_key):
        """Setup API KEY"""

        self.api_key = api_key

    def hit(self, label, **kwargs):
        """Key value level data"""

        payload = kwargs
        payload['label'] = label
        if not 'timestamp' in payload:
            payload['timestamp'] = int(time.time())
        payload['api_key'] = self.api_key
        respone = requests.post('https://a.dashboardspot.com/api-v1/webhook', data=json.dumps(payload))
        return True
