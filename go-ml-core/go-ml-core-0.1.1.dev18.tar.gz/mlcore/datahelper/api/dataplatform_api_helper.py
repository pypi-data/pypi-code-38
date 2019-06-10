from mlcore.datahelper.api.keycloak_sdk import KeycloakSDK
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import base64
import math
import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')




class APIHelper():
    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config['mlcore']['datahelper']['api']['dataplatform']

        self.keycloakSDK = KeycloakSDK(self.config['keycloak'])
        self.keycloak = self.config['keycloak']
        self.access_token = None

        # limit per page
        self.limit_per_page = 200
        self.limit_per_page = {
            'default': 200,
            'nearby_vms': 900
        }

    def get_access_token(self):
        return self.keycloakSDK.get_access_token()

    def logout(self):
        self.keycloakSDK.logout()

    #########################################################
    #
    #   MongoDB API
    #
    #########################################################

    def query_swap_logs(self, cond_dict):
        self.access_token = self.get_access_token()

        data = []
        res = self.query_swap_logs_with_page(cond_dict)

        total_count = res['total_count']
        data = res['data']

        num_page = math.ceil(int(total_count) / float(self.limit_per_page['default']))

        # self.logger.info('total_count = %s' % total_count)
        # self.logger.info('num_page = %s' % num_page)
        # self.logger.info('data = %s' % data)
        # self.logger.info('# of data = %s' % len(data))

        for i in range(1, num_page+1):
            res = self.query_swap_logs_with_page(cond_dict, page=i)
            data = data + res['data']
            # self.logger.info('# of data = %s' % len(data))

        self.logout()

        return data


    def query_swap_logs_with_page(self, cond_dict, page=0):
        url = '%s/swap-logs' % self.config['mongodb-url']

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }

        get_data = {}
        # pagination
        get_data["pagination_criteria"] = {
            "offset": 0 + page * self.limit_per_page['default'],
            "limit": self.limit_per_page['default']
        }
        # essential
        if "exchange_time_start" in cond_dict:
            get_data["exchange_time_start"] = cond_dict["exchange_time_start"]
        if "exchange_time_end" in cond_dict:
            get_data["exchange_time_end"] = cond_dict["exchange_time_end"]
        if "source" in cond_dict:
            get_data["source"] = cond_dict["source"]
        # optinal
        if "create_time_start" in cond_dict:
            get_data["create_time_start"] = cond_dict["create_time_start"]
        if "create_time_end" in cond_dict:
            get_data["create_time_end"] = cond_dict["create_time_end"]
        if "swap_id" in cond_dict:
            get_data["swap_id"] = cond_dict["swap_id"]
        if "vm_guid" in cond_dict:
            get_data["vm_guid"] = cond_dict["vm_guid"]
        if "scooter_guid" in cond_dict:
            get_data["scooter_guid"] = cond_dict["scooter_guid"]

        json_obj = {
            'op_code': 'get',
            'get_data': get_data
        }
        json_option = None

        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        # self.logger.info('pagination_criteria = %s' % get_data["pagination_criteria"])
        
        r = requests.post(url, headers=headers, json=json_obj)
        if json_option is None:
            json_option = {}
        #self.logger.info('r.content = %s' % r.content)
        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res
        else:
            self.logger.warn('Failed to query_swap_logs_with_page: %s', res)
            return None

    def query_vm_status(self, cond_dict):
        self.access_token = self.get_access_token()

        data = []
        res = self.query_vm_status_with_page(cond_dict)

        total_count = res['total_count']
        data = res['data']

        num_page = math.ceil(int(total_count) / float(self.limit_per_page['default']))

        # self.logger.info('total_count = %s' % total_count)
        # self.logger.info('num_page = %s' % num_page)
        # self.logger.info('data = %s' % data)
        # self.logger.info('# of data = %s' % len(data))

        for i in range(1, num_page+1):
            res = self.query_vm_status_with_page(cond_dict, page=i)
            data = data + res['data']
            # self.logger.info('# of data = %s' % len(data))

        self.logout()

        return data

    def query_vm_status_with_page(self, cond_dict, page=0):
        url = '%s/vms/statuses' % self.config['mongodb-url']

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }

        get_data = {}
        # pagination
        get_data["pagination_criteria"] = {
            "offset": 0 + page * self.limit_per_page['default'],
            "limit": self.limit_per_page['default']
        }
        # essential
        if "snap_time_start" in cond_dict:
            get_data["snap_time_start"] = cond_dict["snap_time_start"]
        if "snap_time_end" in cond_dict:
            get_data["snap_time_end"] = cond_dict["snap_time_end"]
        # optinal
        if "state" in cond_dict:
            get_data["state"] = cond_dict["state"]
        if "create_time_start" in cond_dict:
            get_data["create_time_start"] = cond_dict["create_time_start"]
        if "create_time_end" in cond_dict:
            get_data["create_time_end"] = cond_dict["create_time_end"]

        json_obj = {
            'op_code': 'get',
            'get_data': get_data
        }
        json_option = None

        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        # self.logger.info('pagination_criteria = %s' % get_data["pagination_criteria"])
        
        r = requests.post(url, headers=headers, json=json_obj)
        if json_option is None:
            json_option = {}
        #self.logger.info('r.content = %s' % r.content)
        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res
        else:
            self.logger.warn('Failed to query_vm_status_with_page: %s', res)
            return None

    #########################################################
    #
    #   Go Platform API
    #
    #########################################################

    def query_vms(self, vm_ids=None):
        return self.query_vms_v1(vm_ids=vm_ids)


    def query_vms_v1(self, vm_ids=None):
        self.access_token = self.get_access_token()

        data = []
        res = self.query_vms_with_page_v1(vm_ids=vm_ids)

        total_count = res['total_count']
        data = res['data']

        num_page = math.ceil(int(total_count) / float(self.limit_per_page['default']))

        # self.logger.info('total_count = %s' % total_count)
        # self.logger.info('num_page = %s' % num_page)
        # self.logger.info('data = %s' % data)
        # self.logger.info('# of data = %s' % len(data))

        for i in range(1, num_page+1):
            res = self.query_vms_with_page_v1(vm_ids=vm_ids, page=i)
            data = data + res['data']
            # self.logger.info('# of data = %s' % len(data))

        self.logout()

        return data

    def query_vms_with_page_v1(self, vm_ids=None, page=0):
        url = '%s/v1/vms' % self.config['server-url']

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }
        
        if vm_ids==None:
            get_data = {
                'fields_type': 'detail',
                "pagination_criteria": {
                    "offset": 0 + page * self.limit_per_page['default'],
                    "limit": self.limit_per_page['default']
                }
            }
        else:
            get_data = {
                'fields_type': 'detail',
                'vm_ids': vm_ids,
                "pagination_criteria": {
                    "offset": 0 + page * self.limit_per_page['nearby_vms'],
                    "limit": self.limit_per_page['nearby_vms']
                }
            }

        json_obj = {
            'op_code': 'get',
            'get_data': get_data
        }
        json_option = None
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        r = requests.post(url, headers=headers, json=json_obj)
        if json_option is None:
            json_option = {}
        #self.logger.info('r.content = %s' % r.content)
        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res
        else:
            self.logger.warn('Failed to query_vms_with_page_v1: %s', res)

        

    def query_esrates(self):
        return self.query_esrates_v1()

    def query_esrates_v1(self):
        url = '%s/v1/es-rates' % self.config['server-url']

        self.access_token = self.get_access_token()

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }
        json_obj = {
            'op_code': 'get',
            'get_data': {
                'get_flag': 1
            }
        }
        json_option = None
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        r = requests.post(url, headers=headers, json=json_obj)
        if json_option is None:
            json_option = {}
        res = json.loads(r.content.decode('utf-8'),**json_option)

        self.logout()

        if res['code']==0:
            return res['data']
        else:
            self.logger.warn('Failed to query_esrates_v1: %s', res)

    def query_vms_nearby(self):
        return self.query_vms_nearby_v1()


    def query_vms_nearby_v1(self):
        '''
        format of returned nearby-vms 
        
        [
            {
                'vm_id': 'Arm2QMNZ', 
                'nearby_vms': [
                    [{'vm_id': 'Z4mk6rNP', 'distance': 0.35, 'latitude': 25.046688, 'longitude': 121.535175}], 
                    [{'vm_id': 'a6mn7WLo', 'distance': 0.35, 'latitude': 25.046688, 'longitude': 121.535175}], 
                    [{'vm_id': 'WKNv1YR6', 'distance': 0.64, 'latitude': 25.046219, 'longitude': 121.538603}]
                ]
            }
        ]

        '''
        self.access_token = self.get_access_token()

        data = []
        res = self.query_vms_nearby_with_page_v1()

        total_count = res['total_count']
        data = res['data']

        num_page = math.ceil(int(total_count) / float(self.limit_per_page['nearby_vms']))


        # self.logger.info('total_count = %s' % total_count)
        # self.logger.info('num_page = %s' % num_page)
        # self.logger.info('data = %s' % data)
        # self.logger.info('# of data = %s' % len(data))

        for i in range(1, num_page+1):
            res = self.query_vms_nearby_with_page_v1(page=i)
            if len(res['data']) > 0:
                data = data + res['data']
            # self.logger.info('# of data = %s' % len(data))

        key = 'vm_id'
        col = 'nearby_vms'
        # group by vm_id
        nearby_data = {}
        for d in data:
            vm_id = d[key]
            if vm_id in nearby_data:
                nearby_data[vm_id].append(d[col])
            else:
                nearby_data[vm_id] = [d[col]]

        nearby_list = []
        for k,v in nearby_data.items():
            nearby_list.append({key:k, col:v})

        self.logout()

        return nearby_list

    def query_vms_nearby_with_page_v1(self, page=0):
        url = '%s/v1/vms/nearby-vms' % self.config['server-url']

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }
   
        json_obj = {
            'op_code': 'get',
            'get_data': {
                'fields_type': 'detail',
                "pagination_criteria": {
                    "offset": 0 + page * self.limit_per_page['nearby_vms'],
                    "limit": self.limit_per_page['nearby_vms']
                }
            }
        }

        json_option = None
        # print('url=%s' % url)
        # print('header=%s' % headers)
        #print('json=%s' % json_obj)
        r = requests.post(url, headers=headers, json=json_obj)
        #print(r.content)
        if json_option is None:
            json_option = {}

        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res
        else:
            self.logger.warn('Failed to query_vms_nearby_with_page_v1: %s', res)

