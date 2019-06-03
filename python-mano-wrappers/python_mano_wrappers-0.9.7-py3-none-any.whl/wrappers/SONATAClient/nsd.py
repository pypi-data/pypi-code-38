from ..CommonInterface import CommonInterfaceNsd
import json
import requests

class Nsd(CommonInterfaceNsd):
    """
    NSD Management Interfaces
    """

    def __init__(self, host, port=4002):
        self._host = host
        self._port = port
        self._base_path = 'http://{0}:{1}'
        self._user_endpoint = '{0}'

    def get_ns_descriptors(self, token, _filter=None, host=None, port=None):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors:
            GET - Query information about multiple
            NS descriptor resources.

        :param token: auth token retrieved by the auth call
        :param _filter: content query filter 
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_nsd = SONATAClient.Nsd(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)
                _token = json.loads(sonata_auth.auth(
                                        username=USERNAME, 
                                        password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(sonata_nsd.get_ns_descriptors(
                                    token=_token["token"]["access_token"]))
                response = json.loads(response["data"])


        """        
        if host is None:
            base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
            base_path = "http://{0}:{1}".format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type=' + _filter

        _endpoint = "{0}/catalogues/api/v2/network-services{1}".format(base_path, query_path)
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

    def post_ns_descriptors(self, token, package_path, host=None, port=None):
        """ NSD Management Interface - NS Descriptors

        /ns_descriptors:
            POST - Create a new NS descriptor resource.

        :param token: auth token retrieved by the auth call
        :param package_path: file path of the package
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
                sonata_nsd = SONATAClient.Nsd(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                sonata_vnfpkgm.post_vnf_packages(token=_token["token"]["access_token"],
                                    package_path="tests/samples/vnfd_example.yml")

                response = json.loads(sonata_nsd.post_ns_descriptors(
                                    token=_token["token"]["access_token"],
                                    package_path="tests/samples/nsd_example.yml"))


        """

        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
        
    
    def delete_ns_descriptors_nsdinfoid(self, token, nsdinfoid, host=None, port=None):
        """ NSD Management Interface - Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}:
            DELETE - Delete the content of NSD

        :param token: auth token retrieved by the auth call
        :param nsdinfoid: id of the individual NSD
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/x-yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/catalogues/api/v2/network-services/{1}".format(base_path, nsdinfoid)
        
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text        
        return json.dumps(result)        

    def get_ns_descriptors_nsdinfoid(self, token, nsdinfoid, host=None, port=None):
        """ NSD Management Interface -  Individual NS Descriptor

        /ns_descriptors/{nsdInfoId}:
            Read information about an individual NS
            descriptor resource.

        :param token: auth token retrieved by the auth call
        :param nsdinfoid: id of the individual NSD
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
                base_path = "http://{0}:{1}".format(self._host, self._port)
        else:
                base_path = "http://{0}:{1}".format(host, port)
           
        _endpoint = "{0}/catalogues/api/v2/network-services/{1}".format(base_path, nsdinfoid)
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
        
    def patch_ns_descriptors_nsdinfoid(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_ns_descriptors_nsd_content(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def patch_ns_descriptors_nsd_content(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def put_ns_descriptors_nsd_content(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_pnf_descriptors(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
   
    def post_pnf_descriptors(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
 
    def get_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def patch_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def delete_pnf_descriptors_pnfdinfoid(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def put_pnf_descriptors_pnfd_content(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_subscriptions(self, pnfdInfoId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_subscriptions(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
  
    def get_subscriptions_subscriptionid(self, subscriptionid):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def delete_subscriptions_subscriptionid(self, subscriptionid):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)