from ..CommonInterface import CommonInterfaceNslcm
from .helpers import Helpers
import json
import requests
import tarfile

class Nslcm(CommonInterfaceNslcm):
    """
    Lifecycle Management interface
    """
    def __init__(self, host, port=9999):
        self._host = host
        self._port = port
        self._base_path = 'https://{0}:{1}/osm'
        self._user_endpoint = '{0}/admin/v1/users'

    def get_ns_instances(self, token, host=None, port=None):
        """  NS Lifecycle Management interface - 
        NS instances

        /ns_instances:
            GET - Query multiple NS instances.

        :param token: auth token retrieved by the auth call
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                osm_nslcm = OSMClient.Nslcm(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)
                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
                response = json.loads(response["data"])

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/ns_instances_content".format(base_path)
        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_vnf_instances(self, token, host=None, port=None):
        """  NS Lifecycle Management interface - 
        VNF instances - *NON ETSI

        GET - Query multiple VNF instances.

        :param token: auth token retrieved by the auth call
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                osm_nslcm = OSMClient.Nslcm(HOST_URL)
                osm_auth = OSMClient.Auth(HOST_URL)
                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                response = json.loads(osm_nslcm.get_vnf_instances(token=_token["id"]))
                response = json.loads(response["data"])

        """

        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", 
                    "accept": "application/json" ,
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/vnfrs".format(base_path)
        
        try:
            r = requests.get(_endpoint, params=None, verify=False, 
                                headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result

        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)   

    def get_vnf_instances_vnfinstanceid(self, token, vnfInstanceId ,host=None, port=None):
        """  NS Lifecycle Management interface - 
        Individual VNF instance - *NON ETSI

        GET - Read an individual VNF instance resource.

        :param token: auth token retrieved by the auth call
        :param vnfInstanceId: id of the VNF instance        
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)

        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json",
                    "accept": "application/json",
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/vnfrs/{1}".format(base_path, vnfInstanceId)

        try:
            r = requests.get(_endpoint, params=None, verify=False,
                                headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_instantiate(self, token, nsDescription,
                                 nsName, nsdId, vimAccountId, host=None, port=None):
        """  NS Lifecycle Management interface - 
        Instantiate NS task

        /ns_instances_nsinstanceid_instantiate:
            POST - Instantiate a NS instance.

        :param token: auth token retrieved by the auth call
        :param nsDescription: NS instaniation description
        :param nsName: Name for insantiation reference
        :param nsdId: id of the NSD to be instantiate
        :param vimAccountId: ID of the VIM to be instantiated on
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                osm_nsd = OSMClient.Nsd(HOST_URL)
                osm_nslcm = OSMClient.Nslcm(HOST_URL) 
                osm_auth = OSMClient.Auth(HOST_URL)

                _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
                _nsd_list = json.loads(_nsd_list["data"])
                _nsd = None

                for _n in _nsd_list:
                    if "test_osm_cirros_2vnf_nsd" == _n['id']:            
                        _nsd = _n['_id']

                response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_instantiate(token=_token["id"],
                                    nsDescription=NSDESCRIPTION, 
                                    nsName=NSNAME, 
                                    nsdId=_nsd, 
                                    vimAccountId=VIMACCOUNTID))

                response = json.loads(response["data"])

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                        'Authorization': 'Bearer {}'.format(token)}
        ns_data = {"nsDescription": nsDescription, "nsName": nsName,
                        "nsdId": nsdId, "vimAccountId": vimAccountId}                

        _endpoint = "{0}/nslcm/v1/ns_instances_content".format(base_path)

        try:
            r = requests.post(_endpoint, json=ns_data, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def get_ns_instances_nsinstanceid(self, token, nsInstanceId ,host=None, port=None):
        """  NS Lifecycle Management interface - 
        Individual NS instance

        /ns_instances_nsinstanceid:
            GET - Read an individual NS instance resource.

        :param token: auth token retrieved by the auth call
        :param nsInstanceId: id of the NS instance        
        :param host: host url
        :param port: port where the MANO API can be accessed

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/ns_instances_content/{1}".format(base_path, nsInstanceId)

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
   
    def post_ns_instances_nsinstanceid_terminate(self, token, nsInstanceId, host=None, port=None, force=None):
        """  NS Lifecycle Management interface - 
        Terminate NS task

        /ns_instances_nsinstanceid_terminate:
            POST - Terminate a NS instance.

        :param token: auth token retrieved by the auth call
        :param nsInstanceId: id of the NS instance        
        :param host: host url
        :param port: port where the MANO API can be accessed
        :param force: true/false whether to force terminate 
        
        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", "accept": "application/json",
                    'Authorization': 'Bearer {}'.format(token)}
        query_path = ''
        if force:
                query_path = '?FORCE=true'
        _endpoint = "{0}/nslcm/v1/ns_instances_content/{1}{2}".format(base_path, nsInstanceId, query_path)
        try:
            r = requests.delete(_endpoint, params=None, verify=False, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.accepted:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)
   
    def post_ns_instances(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_scale(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
   
    def post_ns_instances_nsinstanceid_update(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def delete_ns_instances_nsinstanceid(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
    
    def post_ns_instances_nsinstanceid_heal(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_ns_lcm_op_ops(self, token, id , host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                        'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/ns_lcm_op_occs/?nsInstanceId={1}".format(base_path, id)

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
                
        result['data'] = r.text
        return json.dumps(result)

    def get_ns_lcm_op_ops_nslcmopoccid(self, token, id , host=None, port=None):
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json", "accept": "application/json",
                        'Authorization': 'Bearer {}'.format(token)}
        _endpoint = "{0}/nslcm/v1/ns_lcm_op_occs/{1}".format(base_path, id)

        try:
            r = requests.get(_endpoint, params=None, verify=False, stream=True, headers=headers)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.ok:
            result['error'] = False
                
        result['data'] = r.text
        return json.dumps(result)
    
    def post_ns_lcm_op_occs_nslcmopoccid_retry(self, nsLcmOpOccId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_lcm_op_occs_nslcmopoccid_rollback(self, nsLcmOpOccId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_lcm_op_occs_nslcmopoccid_continue(self, nsLcmOpOccId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_lcm_op_occs_nslcmopoccid_fail(self, nsLcmOpOccId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_lcm_op_occs_nslcmopoccid_cancel(self, nsLcmOpOccId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def post_ns_lcm_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_ns_lcm_subscriptions(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    def get_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)
   
    def delete_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}
        return json.dumps(result)

    # def get_unknown(self):
    #     """  NS Lifecycle Management interface - 
    #             Notification endpoint

    #     /unknown
    #         GET - Test the notification endpoint.

    #     """
    #     pass


    
    # def post_unknown(self):
    #     """  NS Lifecycle Management interface - 
    #             Notification endpoint

    #     /unknown
    #         POST - Notify about NS lifecycle change.

    #     """
    #     pass