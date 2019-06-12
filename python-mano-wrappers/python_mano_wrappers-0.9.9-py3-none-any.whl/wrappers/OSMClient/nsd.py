from ..CommonInterface import CommonInterfaceNsd
from .helpers import Helpers
import json
import requests

class Nsd(CommonInterfaceNsd):
    """
    NSD Management Interfaces
    """

    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

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

                osm_nsd = OSMClient.Nsd(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)

                _token = json.loads(osm_auth.auth(
                                        username=USERNAME,
                                        password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(osm_nsd.get_ns_descriptors(
                                        token=_token["id"]))
                response = json.loads(response["data"])

        """        
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        query_path = ''
        if _filter:
            query_path = '?_admin.type=' + _filter

        _endpoint = "{0}/nsd/v1/ns_descriptors_content{1}".format(base_path, query_path)
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

                osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
                osm_nsd = OSMClient.Nsd(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)
                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                    package_path="tests/samples/test_osm_cirros_vnfd.tar.gz")

                response = json.loads(osm_nsd.post_ns_descriptors(token=_token["id"],
                                    package_path="tests/samples/test_osm_cirros_nsd.tar.gz"))
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
        _endpoint = "{0}/nsd/v1/ns_descriptors_content/".format(base_path)
        try:
            r = requests.post(_endpoint, data=open(package_path, 'rb'), verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
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

        Example:
            .. code-block:: python
            
                osm_nsd = OSMClient.Nsd(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)

                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _nsd = "24d8ea1c-3d96-47d6-8fc4-473c9a6f1ad2"

                response = json.loads(osm_nsd.get_ns_descriptors_nsdinfoid(
                                            token=_token["id"], nsdinfoid=_nsd))


        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd".format(base_path, nsdinfoid)
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

    def patch_ns_descriptors_nsdinfoid(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
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
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                   'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/nsd/v1/ns_descriptors_content/{1}".format(base_path, nsdinfoid)

        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.no_content:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
    
    def get_ns_descriptors_nsd_content(self, token, nsdinfoid, host=None, port=None):
        """ NSD Management Interface - NSD Content
        
        /ns_descriptors/{nsdInfoId}/nsd_c:
            GET - Fetch the content of a NSD.

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
        headers = {"accept": "application/zip",
                    'Authorization': 'Bearer {}'.format(token)}

        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(base_path, nsdinfoid)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def put_ns_descriptors_nsd_content(self, token, data_path, nsdinfoid, host=None, port=None):
        """ NSD Management Interface - NSD Content
        
        /ns_descriptors/{nsdInfoId}/nsd_c:
            PUT - Upload the content of NSD

        :param token: auth token retrieved by the auth call
        :param data_path: file location of the NSD 
        :param nsdinfoid: id of the individual NSD
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

        _endpoint = "{0}/nsd/v1/ns_descriptors/{1}/nsd_content".format(base_path, nsdinfoid)

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