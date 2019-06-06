from ..CommonInterface import CommonInterfaceVnfPkgm
import json
import requests

class VnfPkgm(CommonInterfaceVnfPkgm):
    """
    VNF Package Management Interfaces
    """
    
    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'

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

        _endpoint = "{0}/catalogues/api/v2/vnfs{1}".format(base_path,query_path)
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

                sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(sonata_vnfpkgm.post_vnf_packages(
                                        token=_token["token"]["access_token"],
                                        package_path="tests/samples/vnfd_example.yml"))

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/vnfs".format(base_path)
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
       
        _endpoint = "{0}/catalogues/api/v2/vnfs{1}".format(base_path, vnfPkgId)
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
        headers = {"Content-Type": "application/x-yaml", 'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/catalogues/api/v2/vnfs/{1}".format(base_path, vnfPkgId)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_vnf_packages_vnfpkgid_vnfd(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def put_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_vnf_packages_vnfpkgid_package_content(self, vnfPkgId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_vnf_packages_vnfpkgid_artifacts_artifactpath(self, 
            vnfPkgId, artifactPath):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_vnf_packages_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_vnf_packages_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)