'''
functions for mocking connection to cortex for testing 
'''


import json

from mocket.mockhttp import Entry


def john_doe_token():
    '''token with user name John Doe, this is a
        slight modification to the default at
        https://jwt.io/ debugger, with this json
        payload:
        {
         "sub": "1234567890",
         "name": "John Doe",
         "iat": 1516239022,
         "tenant": "Acme Inc."
        }
    '''
    return 'eyJhbGciOiJIUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJ0ZW5hbnQiOiJBY21lIEluYy4ifQ.ky4VnJ8kZnShc1Tk6oqat1SYUvSeiCMD3_GWckrKPJFq600Y-Zxa1lZi_YLuHRX6'


def john_doe_subject():
    '''
    The subject part of the jwt token
    '''
    return '1234567890'


def build_mock_url(uri, version=3):
    '''
    build a mock url for testing
    '''
    return "{api_endpoint}/v{version}/{uri}".format(api_endpoint=mock_api_endpoint(), version=version, uri=uri)


def mock_api_endpoint():
    '''
    the url endppoint for mocking
    '''
    return 'http://1.2.3.4:8000'


def register_entry(verb, url, body:dict):
    print('Registering mock for', verb, url)
    Entry.single_register(verb, url, status=200, body=json.dumps(body))


def register_entry_from_path(verb, url, path:str):
    with open(path) as fh:
        register_entry(verb, url, json.load(fh))
