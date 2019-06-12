from ..CommonInterface import CommonInterfaceSonPackage
# from .helpers import Helpers
import json
import requests

class Package(CommonInterfaceSonPackage):

    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'

    def get_son_packages(self, token, _filter=None, host=None, port=None):
        if host is None:
            base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
            base_path = "http://{0}:{1}".format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type=' + _filter

        _endpoint = "{0}/catalogues/api/v2/son-packages{1}".format(base_path, query_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(token)}

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_son_packages(self, token, package_path, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-www-form-urlencoded", 
                    "Content-Disposition": "attachment; filename=sonata_example.son", 
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/son-packages".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        
    def delete_son_packages_PackageId(self, token, id, host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/son-packages/{1}".format(base_path, id)
        
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text        
        return json.dumps(result)        

    def get_son_packages_PackageId(self, token, id, host=None, port=None):
        if host is None:
            base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
            base_path = "http://{0}:{1}".format(host, port)

        _endpoint = "{0}/catalogues/api/v2/son-packages{1}".format(base_path, id)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", 'Authorization': 'Bearer {}'.format(token)}

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)