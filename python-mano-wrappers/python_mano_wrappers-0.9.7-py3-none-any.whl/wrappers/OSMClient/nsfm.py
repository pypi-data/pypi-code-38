from ..CommonInterface import CommonInterfaceNsfm
from .helpers import Helpers
import json
import requests
import tarfile

class Nsfm(CommonInterfaceNsfm):

    def get_nsfm_alarms(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_nsfm_alarms_alarmid(self, alarmId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def patch_nsfm_alarms_alarmid(self, alarmId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_nsfm_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_nsfm_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_nsfm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def delete_nsfm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)


    # 
    # def get_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         GET - Test the notification endpoint.

    #     """
    #     pass


    # 
    # def post_nsfm_unknown(self):
    #     """  NS Fault Management interface - 
    #             Notification endpoint

    #     /nsfm_unknown
    #         POST - Notify about NS alarms.

    #     """
    #     pass