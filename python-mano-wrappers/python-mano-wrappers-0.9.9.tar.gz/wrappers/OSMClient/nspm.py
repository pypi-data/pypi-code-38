from ..CommonInterface import CommonInterfaceNslcm
from .helpers import Helpers
import json
import requests
import tarfile


def get_pm_jobs(self):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def post_pm_jobs(self):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_jobs_pmjobid(self, pmJobId):
   
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def delete_pm_jobs_pmjobid(self, pmJobId):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_jobs_pmjobid_reports_reportid(self, pmJobId, reportId):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_thresholds(self):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def post_pm_thresholds(self):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_thresholds_thresholdid(self, thresholdId):
   
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def delete_pm_thresholds_thresholdid(self, thresholdId):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_subscriptions(self):

    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def post_pm_subscriptions(self):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def get_pm_subscriptions_subscriptionid(self, subscriptionId):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)


def delete_pm_subscriptions_subscriptionid(self, subscriptionId):
    
    result = {'error': True, 'data': 'Method not implemented in target MANO'}     
    return json.dumps(result)

    # 
    # def get_unknown(sfrom ..CommonInterface import CommonInterfaceNslcm

    #     """ NS Performance Management Interface - 
    #             Notification endpoint

    #     /unknown
    #         GET - Test the notification endpoint

    #     """
    #     result = {'error': True, 'data': 'Method not implemented in target MANO'}     return json.dumps(result)

    # 
    # def post_unknown(self):
    #     """ NS Performance Management Interface - 
    #             Notification endpoint

    #     /unknown
    #         POST - Notify about PM related events

    #     """
    #     result = {'error': True, 'data': 'Method not implemented in target MANO'}     return json.dumps(result)