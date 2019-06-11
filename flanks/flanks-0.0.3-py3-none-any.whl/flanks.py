import requests
import json


class Flanks():
    access_key = ''
    dns = ''
    session = ''
    
    def __init__(self, auth, env='sandbox'):
        '''
        Initialize a client with oauth

        :arg str auth: Your oauth token from Flanks
        :arg str env: One of ``sandbox``, ``development``, or ``production`` 
        '''

        self.access_key = auth 
        self.dns = 'https://'+'sandbox' +'.flanks.io'
        self.session = requests.Session()
        headers = {
            'Content-Type': "application/json",
            'Pragma': "no-cache",
            'cache-control': "no-cache",
            'Authorization': "Bearer " + auth,
        }
        self.session.headers.update(headers)

    def create_user(self,username, password, bank, verifier=None):
        '''
        Create client in Flanks's system

        :arg str username: Username of online bank platform
        :arg str password: Password of online bank platform
        :arg str bank: Name of bank entity
        :arg str verifier: Extra argument of the bank's platform credential
        '''
        data = {
            'username': username,
            'password': password,
            'bank': bank,
            'verifier': verifier
        }
        r = self.session.post(self.dns + '/v0/bank/credentials', data=json.dumps(data))
        if not 'credentials_token' in r.json():
            raise Exception(r.content)
        return r.json()['credentials_token']

    
    def get_one_shot(self,username, password, bank, query=None,password2=None):
        '''
        Transactions data from Bank Platform

        :arg str username: Username of online bank platform
        :arg str password: Password of online bank platform
        :arg str bank: Name of bank entity
        :arg obj query: Query of bank entity
        :arg str verifier: Extra argument of the bank's platform credential
        '''
        if(not query):
            data = {
                'username': username,
                'password': password,
                'bank': bank,
                'verifier': password2,
            }
        else:
            data = {
                'username': username,
                'password': password,
                'bank': bank,
                'verifier': password2,
                'query': query
            }

        r = self.session.post(self.dns + '/v0/bank/credentials/data', data=json.dumps(data))
        if 'message' in r.json():
            raise Exception(r.json()['message'])
        return r.json()
    
    def get_data(self,credentials_token):
        '''
        Transactions data from Bank Platform

        :arg str credentials_token: Credentials attached to user credentials of bank platform
        '''
        data = {
            "credentials_token": credentials_token,
        }
        r = self.session.post(self.dns + '/v0/bank/credentials/data', data=json.dumps(data))
        if 'message' in r.json():
            raise Exception(r.json()['message'])
        return r.json()


    def delete_user(self,credentials_token):
        '''
        Delete user from the system

        :arg str credentials_token: Credentials attached to user credentials of bank platform
        '''
        data = {
            "credentials_token": credentials_token,
        }
        r = self.session.delete(self.dns + '/v0/bank/credentials', data=json.dumps(data))
        return r.json()['message'] 

