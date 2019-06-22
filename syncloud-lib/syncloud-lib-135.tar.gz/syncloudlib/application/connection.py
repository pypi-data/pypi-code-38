import requests_unixsocket
import json
import os

socket_file = '/var/snap/platform/common/api.socket'
socket = 'http+unix://{0}'.format(socket_file.replace('/', '%2F'))


def api_post(url, data):
    session = requests_unixsocket.Session()
    try:
        response = session.post('{0}{1}'.format(socket, url), data=data)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if 'success' in response_json and response_json['success']:
                return response_json['data']
            else:
                raise Exception('service error: {0}'.format(response_json['message']))
            
        else:
            raise Exception('unable to connect to {0} with error code: {1}'.format(socket, response.status_code))
    except Exception, e:
        raise Exception('unable to connect to {0}'.format(socket), e)


def api_get(url):
    session = requests_unixsocket.Session()
    try:
        response = session.get('{0}{1}'.format(socket, url))
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if 'success' in response_json and response_json['success']:
                return response_json['data']
            else:
                raise Exception('service error: {0}'.format(response_json['message']))
            
        else:
            raise Exception('unable to connect to {0} with error code: {1}'.format(socket, response.status_code))
    except Exception, e:
        raise Exception('unable to connect to {0}'.format(socket), e)
