import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import base64
import ast
import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')



def str_to_dict(str):
    str = str.replace('false', 'False')
    str = str.replace('true', 'True')
    return ast.literal_eval(str)

keycloak_json = {
    "realm": "gogoro",
    "auth-server-url": "https://auth.gogoro.com:8443",
    "resource": "machine_learning",
    "credentials": {
        "secret": "63dbf6a1-0173-4692-b733-889aa70935d3"
    }
}

class KeycloakSDK():

    def __init__(self, keycloak):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.keycloak = keycloak
        self.token = None

    def get_access_token(self):
        # 1. service_account_login
        self.service_account_login()
        # 2. get_authorization
        self.get_authorization()
        # 3. refresh_access_token (schedule)
        #self.refresh_access_token()
        
        return self.token['access_token']

    def service_account_login(self):
        '''
        Service Account Login
        Method : basicAuth(resource, serviceConfig)
        '''

        url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.keycloak["auth-server-url"], self.keycloak["realm"])
        
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Authorization': 'Basic %s' % base64.b64encode(bytes('%s:%s'% (self.keycloak["resource"], self.keycloak["credentials"]["secret"]),'utf-8')).decode("utf-8")
        }
        payload = {
            'grant_type' : 'client_credentials'
        }
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('data=%s' % payload)
        response = requests.post(url, headers=headers, data=payload, verify=False).text
        
        self.token = str_to_dict(response)

    def get_authorization(self): 
        '''
        GetAuthorization
        Description: Use following information to get authorization. resource 為目標要取得的 application resource
        '''
        
        url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.keycloak["auth-server-url"], self.keycloak["realm"]) 
        
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer %s' % self.token['access_token']
        }
        payload = {
            'grant_type' : 'urn:ietf:params:oauth:grant-type:uma-ticket',
            'audience' : self.keycloak["resource"]
        }
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('data=%s' % payload)
        response = requests.post(url, headers=headers, data=payload, verify=False).text
        
        self.token = str_to_dict(response)

    def refresh_access_token(self):
        '''
        RefreshGrant
        Method refreshGrant(grant)
        '''

        url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.auth_server_url, self.realm) 
        
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Authorization': 'Basic %s' % base64.b64encode(bytes('%s:%s'% (self.resource, self.secret),'utf-8')).decode("utf-8")
        }
        payload = {
            'client_id': self.resource,
            'refresh_token' : self.token['refresh_token'],
            'grant_type' : 'refresh_token'
        }
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('data=%s' % payload)
        response = requests.post(url, headers=headers, data=payload, verify=False).text
        
        self.token = str_to_dict(response)

class APIHelper():
    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config['mlcore']['datahelper']['api']['dataplatform']

        self.keycloakSDK = KeycloakSDK(self.config['keycloak'])
        self.keycloak = self.config['keycloak']
        self.access_token = None


    def get_access_token(self):
        return self.keycloakSDK.get_access_token()

    def query_vms(self):
        return self.query_vms_v1()

    def query_vms_v1(self):
        url = '%s/v1/vms' % self.config['server_url']

        self.access_token = self.get_access_token()

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }
        json_obj = {
            'op_code': 'get',
            'get_data': {
                'fields_type': 'detail'
            }
        }
        json_option = None
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        r = requests.post(url, headers=headers, json=json_obj)
        # print(r)
        if json_option is None:
            json_option = {}
        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res['data']
        else:
            self.logger.warn('Failed to query_vms_v1: %s', res)

    def query_esrates(self):
        return self.query_esrates_v1()

    def query_esrates_v1(self):
        url = '%s/v1/es-rates' % self.config['server_url']

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
        # print(r)
        if json_option is None:
            json_option = {}
        res = json.loads(r.content.decode('utf-8'),**json_option)

        if res['code']==0:
            return res['data']
        else:
            self.logger.warn('Failed to query_vms_v1: %s', res)

    def query_vms_nearby(self):
        return self.query_vms_nearby_v1()

    def query_vms_nearby_v1(self):
        url = '%s/v1/vms/nearby-vms' % self.config['server_url']
         
        self.access_token = self.get_access_token()

        headers = {
            'Go-Client':self.keycloak['resource'],
            'Authorization':'Bearer {}'.format(self.access_token),
        }
        json_obj = {
            'op_code': 'get',
            'get_data': {
                'fields_type': 'detail'
            }
        }
        json_option = None
        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('json=%s' % json_obj)
        r = requests.post(url, headers=headers, json=json_obj)
        print(r.content)
        if json_option is None:
            json_option = {}
        return json.loads(r.content.decode('utf-8'),**json_option)

# class KeycloakSDK():

#     def __init__(
#         self,
#         logger=None,
#         keycloak_str=''):
#         if keycloak_str=='':
#             global keycloak_json
#             keycloak = keycloak_json
#         else:
#             keycloak = json.loads(keycloak_str)
#         self.realm = keycloak["realm"]
#         self.auth_server_url = keycloak["auth-server-url"]
#         self.resource = keycloak["resource"]
#         self.secret = keycloak["credentials"]["secret"]
#         self.token = None
    
#     def get_access_token(self):
#         # 1. service_account_login
#         self.service_account_login()
#         # 2. get_authorization
#         self.get_authorization()
#         # 3. refresh_access_token (schedule)
#         #self.refresh_access_token()
        
#         return self.token['access_token']

#     def service_account_login(self):
#         '''
#         Service Account Login
#         Method : basicAuth(resource, serviceConfig)
#         '''

#         url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.auth_server_url, self.realm )
        
#         headers = {
#             'Content-Type' : 'application/x-www-form-urlencoded',
#             'Authorization': 'Basic %s' % base64.b64encode(bytes('%s:%s'% (self.resource, self.secret),'utf-8')).decode("utf-8")
#         }
#         payload = {
#             'grant_type' : 'client_credentials'
#         }
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('data=%s' % payload)
#         response = requests.post(url, headers=headers, data=payload, verify=False).text
        
#         self.token = str_to_dict(response)

#     def get_authorization(self): 
#         '''
#         GetAuthorization
#         Description: Use following information to get authorization. resource 為目標要取得的 application resource
#         '''
        
#         url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.auth_server_url, self.realm) 
        
#         headers = {
#             'Content-Type' : 'application/x-www-form-urlencoded',
#             'Authorization': 'Bearer %s' % self.token['access_token']
#         }
#         payload = {
#             'grant_type' : 'urn:ietf:params:oauth:grant-type:uma-ticket',
#             'audience' : self.resource
#         }
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('data=%s' % payload)
#         response = requests.post(url, headers=headers, data=payload, verify=False).text
        
#         self.token = str_to_dict(response)

#     def refresh_access_token(self):
#         '''
#         RefreshGrant
#         Method refreshGrant(grant)
#         '''

#         url = '%s/auth/realms/%s/protocol/openid-connect/token' % (self.auth_server_url, self.realm) 
        
#         headers = {
#             'Content-Type' : 'application/x-www-form-urlencoded',
#             'Authorization': 'Basic %s' % base64.b64encode(bytes('%s:%s'% (self.resource, self.secret),'utf-8')).decode("utf-8")
#         }
#         payload = {
#             'client_id': self.resource,
#             'refresh_token' : self.token['refresh_token'],
#             'grant_type' : 'refresh_token'
#         }
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('data=%s' % payload)
#         response = requests.post(url, headers=headers, data=payload, verify=False).text
        
#         self.token = str_to_dict(response)


# class URLHelper():
#     def __init__(
#         self,
#         logger=None,
#         config_file='go_servers.ini',
#         host_name='DataPlatform_DEV_API'):
#         self.logger = logger
#         self.config_file = config_file
#         self.host_name = host_name

#         self.config = configparser.ConfigParser()
#         self.config.read(self.config_file)

#         self.keycloak = KeycloakSDK(
#             logger=logger, 
#             keycloak_str=self.config[self.host_name]['keycloak'])


#     def get_access_token(self):
#         return self.keycloak.get_access_token()

#     def query_vms(self):
#         return self.query_vms_v1()

#     def query_vms_nearby(self):
#         return self.query_vms_nearby_v1()

#     def query_vms_nearby_v1(self):
#         url = '%s/v1/vms/nearby-vms' % self.config[self.host_name]['server_url']
         
#         self.access_token = self.get_access_token()

#         headers = {
#             'Go-Client':self.keycloak.resource,
#             'Authorization':'Bearer {}'.format(self.access_token),
#         }
#         json_obj = {
#             'op_code': 'get',
#             'get_data': {
#                 'fields_type': 'detail'
#             }
#         }
#         json_option = None
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('json=%s' % json_obj)
#         r = requests.post(url, headers=headers, json=json_obj)
#         print(r.content)
#         if json_option is None:
#             json_option = {}
#         return json.loads(r.content.decode('utf-8'),**json_option)

#     def query_vms_v1(self):
#         url = '%s/v1/vms' % self.config[self.host_name]['server_url']

#         self.access_token = self.get_access_token()

#         headers = {
#             'Go-Client':self.keycloak.resource,
#             'Authorization':'Bearer {}'.format(self.access_token),
#         }
#         json_obj = {
#             'op_code': 'get',
#             'get_data': {
#                 'fields_type': 'detail'
#             }
#         }
#         json_option = None
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('json=%s' % json_obj)
#         r = requests.post(url, headers=headers, json=json_obj)
#         # print(r)
#         if json_option is None:
#             json_option = {}
#         res = json.loads(r.content.decode('utf-8'),**json_option)

#         if res['code']==0:
#             return res['data']
#         else:
#             self.logger.warn('Failed to query_vms_v1: %s', res)

#     def query_esrates(self):
#         return self.query_esrates_v1()

#     def query_esrates_v1(self):
#         url = '%s/v1/es-rates' % self.config[self.host_name]['server_url']

#         self.access_token = self.get_access_token()

#         headers = {
#             'Go-Client':self.keycloak.resource,
#             'Authorization':'Bearer {}'.format(self.access_token),
#         }
#         json_obj = {
#             'op_code': 'get',
#             'get_data': {
#                 'get_flag': 1
#             }
#         }
#         json_option = None
#         # print('url=%s' % url)
#         # print('header=%s' % headers)
#         # print('json=%s' % json_obj)
#         r = requests.post(url, headers=headers, json=json_obj)
#         # print(r)
#         if json_option is None:
#             json_option = {}
#         res = json.loads(r.content.decode('utf-8'),**json_option)

#         if res['code']==0:
#             return res['data']
#         else:
#             self.logger.warn('Failed to query_vms_v1: %s', res)


