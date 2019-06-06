import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
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

        self.logger.info('Service account login: %s' % self.token['access_token'])

        return self.token['access_token']

    def service_account_login(self):
        '''
        Service Account Login
        Method : basicAuth(resource, serviceConfig)
        '''

        url = '%s/realms/%s/protocol/openid-connect/token' % (self.keycloak["auth-server-url"], self.keycloak["realm"])
        
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

    def logout(self):
        '''
        Logout
        '''
        url = '%s/realms/%s/protocol/openid-connect/logout' % (self.keycloak["auth-server-url"], self.keycloak["realm"])
        
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Authorization': 'Basic %s' % base64.b64encode(bytes('%s:%s'% (self.keycloak["resource"], self.keycloak["credentials"]["secret"]),'utf-8')).decode("utf-8")
        }

        payload = {
            'refresh_token' : self.token['refresh_token']
        }

        # print('url=%s' % url)
        # print('header=%s' % headers)
        # print('data=%s' % payload)

        response = requests.post(url, headers=headers, data=payload, verify=False)

        if response.status_code == 204:
            self.logger.info('Logout successfully: %s' % response.text)
            #self.logger.info('Logout successfully.')
            return
        else:
            self.logger.warn('Logout failed: %s' % response.text)


    def get_authorization(self): 
        '''
        GetAuthorization
        Description: Use following information to get authorization. resource 為目標要取得的 application resource
        '''
        
        url = '%s/realms/%s/protocol/openid-connect/token' % (self.keycloak["auth-server-url"], self.keycloak["realm"]) 
        
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

        url = '%s/realms/%s/protocol/openid-connect/token' % (self.auth_server_url, self.realm) 
        
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