from mlcore.datahelper.api.keycloak_sdk import KeycloakSDK
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import base64
import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')
                    
class APIHelper():

    def __init__(self, config):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config['mlcore']['datahelper']['api']['mongodb']

        self.keycloakSDK = KeycloakSDK(self.config['keycloak'])
        self.keycloak = self.config['keycloak']
        self.access_token = None

    def get_access_token(self):
        return self.keycloakSDK.get_access_token()

    