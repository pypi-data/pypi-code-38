from ..CommonInterface import CommonInterfaceVnfPkgm
from .helpers import Helpers
import json
import requests
import tarfile

class VnfPkgm(CommonInterfaceVnfPkgm):
    """
    VNF Package Management Interfaces
    """
    
    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

    def get_vnf_packages(self, token, _filter=None, host=None, port=None):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages:
            GET - Query VNF packages information

        :param token: auth token retrieved by the auth call
        :param _filter: content query filter 
        :param host: host url
        :param port: port where the MANO API can be accessed

        """

        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type='+_filter

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content".format(base_path, query_path)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
        
        result['data'] = r.text
        return json.dumps(result)
  
    def post_vnf_packages(self, token, package_path, host=None, port=None):
        """ VNF Package Management Interface - VNF packages

        /vnf_packages:
            POST - Create a new individual 
            VNFpackage resource

        :param token: auth token retrieved by the auth call
        :param package_path: file path of the package
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)

                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                                    package_path="tests/samples/test_osm_cirros_vnfd.tar.gz"))
                response = json.loads(response["data"])

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                     'Authorization': 'Bearer {}'.format(token),
                     'Content-File-MD5': Helpers.md5(open(package_path, 'rb'))}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_vnf_packages_vnfpkgid(self, token, vnfPkgId, host=None, port=None):
        """ VNF Package Management Interface - 
        Individual VNF package

        /vnf_packages/{vnfPkgId}:
            GET - Read information about an 
            individual VNF package
   
        :param token: auth token retrieved by the auth call
        :param vnfPkgId: id of the vnf package to fetch
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                        'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(base_path, vnfPkgId)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
    
    def patch_vnf_packages_vnfpkgid(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def delete_vnf_packages_vnfpkgid(self, token, vnfPkgId, host=None, port=None):
        """ VNF Package Management Interface - 
        Individual VNF package

        /vnf_packages/{vnfPkgId}:
            DELETE - Delete an individual VNF package

        :param token: auth token retrieved by the auth call
        :param vnfPkgId: id of the vnf package to fetch
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages_content/{1}".format(base_path, vnfPkgId)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)       
 
    def get_vnf_packages_vnfpkgid_vnfd(self, token, vnfPkgId , host=None, port=None):
        """ VNF Package Management Interface - 
        VNFD of an individual VNF package

        /vnf_packages/{vnfPkgId}/vnfd:
            GET - Read VNFD of an on-boarded VNF package

        :param token: auth token retrieved by the auth call
        :param vnfPkgId: id of the vnf package to delete
        :param host: host url
        :param port: port where the MANO API can be accessed
   
        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/vnfd".format(base_path, vnfPkgId)
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml',
                        'Authorization': 'Bearer {}'.format(token)}
                
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
                
        result['data'] = r.text
        return json.dumps(result)

    def get_vnf_packages_vnfpkgid_package_content(self, token, vnfPkgId ,host=None, port=None):
        """ VNF Package Management Interface - 
        VNF package content

        /vnf_packages/{vnfPkgId}/package_content:
            GET - Fetch an on-boarded VNF package

        :param token: auth token retrieved by the auth call
        :param vnfPkgId: id of the vnf package to delete
        :param host: host url
        :param port: port where the MANO API can be accessed
      
        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"accept": "application/zip",
                'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(base_path, vnfPkgId)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
    
    def put_vnf_packages_vnfpkgid_package_content(self, token, data_path, vnfPkgId, host=None, port=None):
        """ VNF Package Management Interface - 
        VNF package content

        /vnf_packages/{vnfPkgId}/package_content:
            PUT - Upload a VNF package by providing 
            the content of the VNF package

        :param token: auth token retrieved by the auth call
        :param data_path: file location of the VNFD 
        :param vnfPkgId: id of the vnf package to delete
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        
        headers = {"Content-Type": "application/gzip", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token),
                    'Content-File-MD5': Helpers.md5(open(data_path, 'rb'))}

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/package_content".format(base_path, vnfPkgId)
        
        try:
            r = requests.put(_endpoint, data=open(data_path, 'rb'), verify=False,
                            headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        
    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, token, vnfPkgId , host=None, port=None):
        """ VNF Package Management Interface - 
        Individual VNF package artifact

        /vnf_packages/{vnfPkgId}/artifacts/{artifactPath}:
            GET - Fetch individual VNF package artifact

        :param token: auth token retrieved by the auth call
        :param vnfPkgId: id of the vnf package to delete
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        _endpoint = "{0}/vnfpkgm/v1/vnf_packages/{1}/artifacts".format(base_path, vnfPkgId)
        result = {'error': True, 'data': ''}
        headers = {'Content-Type': 'application/yaml', 'accept': 'text/plain',
                'Authorization': 'Bearer {}'.format(token)}
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    
    def get_vnf_packages_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
  
    def post_vnf_packages_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
