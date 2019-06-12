from ..CommonInterface import CommonInterfaceNslcm
# from .helpers import Helpers
import json
import requests
# import tarfile

class Nslcm(CommonInterfaceNslcm):
    """
    Lifecycle Management interface
    """
    def __init__(self, host, port=32001, repositories_port=4002):
        self._host = host
        self._port = port
        self._repositories_port = repositories_port
        self._base_path = 'http://{0}:{1}/api/v2'
        self._repositories_base_path = 'http://{0}:{1}/'
        
    def get_ns_instances(self, token, offset=None, limit=None, host=None, port=None):
        """  NS Lifecycle Management interface - 
        NS instances

        /ns_instances:
            GET - Query multiple NS instances.

        :param token: auth token retrieved by the auth call
        :param offset: offset index while returning
        :param limit: limit records while returning
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)
                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])
                response = json.loads(sonata_nslcm.get_ns_instances(
                                        token=_token["token"]["access_token"]))
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
        
        if not offset:
            offset = 0
        if not limit:
            limit = 10

        _endpoint = "{0}/records/services?offset={1}&limit={2}".format(base_path, offset, limit)
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
        headers = {"Content-Type": "application/json",
                    "accept": "application/json",
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/records/services/{1}".format(base_path, nsInstanceId)

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

    def get_vnf_instances(self, token, offset=None, limit=None, host=None, port=None):
        """  NS Lifecycle Management interface - 
        VNF instances - *NON ETSI

        GET - Query multiple VNF instances.

        :param token: auth token retrieved by the auth call
        :param offset: offset index while returning
        :param limit: limit records while returning
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)
                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])
                response = json.loads(sonata_nslcm.get_vnf_instances(
                                        token=_token["token"]["access_token"]))
                response = json.loads(response["data"])            

        """

        if host is None:
            base_path = self._repositories_base_path.format(self._host, self._repositories_port)
        else:
            base_path = self._repositories_base_path.format(host, port)
        
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/yaml", 
                    "accept": "application/json" ,
                    "Authorization": 'Bearer {}'.format(token)}

        if not offset:
            offset = 0
        if not limit:
            limit = 10

        _endpoint = "{0}/records/vnfr/vnf-instances?offset={1}&limit={2}".format(base_path, offset, limit)

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
            base_path = self._repositories_base_path.format(self._host, self._repositories_port)
        else:
            base_path = self._repositories_base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {"Content-Type": "application/json",
                    "accept": "application/json",
                    "Authorization": 'Bearer {}'.format(token)}
        _endpoint = "{0}/records/vnfr/vnf-instances/{1}".format(base_path, vnfInstanceId)

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


    def post_ns_instances_nsinstanceid_instantiate(self, token, nsInstanceId, egresses=[], ingresses=[], host=None, port=None):
        """  NS Lifecycle Management interface - 
        Instantiate NS task

        /ns_instances_nsinstanceid_instantiate:
            POST - Instantiate a NS instance.

        :param token: auth token retrieved by the auth call
        :param nsInstanceId: NS instaniation description
        :param ingresses: ingresses list
        :param egresses: egresses list 
        :param host: host url
        :param port: port where the MANO API can be accessed

        Example:
            .. code-block:: python

                sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
                sonata_auth = SONATAClient.Auth(HOST_URL)
                sonata_nsd = SONATAClient.Nsd(HOST_URL)

                _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
                _token = json.loads(_token["data"])

                _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(token=_token["token"]["access_token"]))
                _nsd_list = json.loads(_nsd_list["data"])

                _ns = None
                for _n in _nsd_list:
                    if "A dummy Example." == _n['nsd']['description']:            
                        _ns = _n['uuid']

                if _ns:
                    response = json.loads(
                                sonata_nslcm.post_ns_instances_nsinstanceid_instantiate(
                                    token=_token["token"]["access_token"], nsInstanceId=_ns))

        """
        if host is None:
            base_path = self._base_path.format(self._host, self._port)
        else:
            base_path = self._base_path.format(host, port)
        result = {'error': True, 'data': ''}
        headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": 'Bearer {}'.format(token)}
        data = {
                "service_uuid": nsInstanceId,
                "egresses" : egresses,
                "ingresses" : ingresses
        }
        _endpoint = "{0}/requests".format(base_path)

        try:
            r = requests.post(_endpoint, params=None, verify=False,
                                headers=headers, json=data)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_terminate(self, token, nsInstanceId, host=None, port=None):
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
        headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": 'Bearer {}'.format(token)}

        data = {
                "service_instance_uuid": nsInstanceId,
                "request_type": "TERMINATE"
        }

        _endpoint = "{0}/requests".format(base_path)

        try:
            r = requests.post(_endpoint, params=None, verify=False,
                                headers=headers, json=data)
        except Exception as e:
            result['data'] = str(e)
            return result
        if r.status_code == requests.codes.created:
            result['error'] = False

        result['data'] = r.text
        return json.dumps(result)

    def post_ns_instances_nsinstanceid_scale(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)
   
    def post_ns_instances_nsinstanceid_update(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)
    
    def post_ns_instances_nsinstanceid_heal(self, nsInstanceId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
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

    def delete_ns_instances_nsinstanceid(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)

    def get_ns_lcm_op_ops(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)

    def get_ns_lcm_op_ops_nslcmopoccid(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)

    def post_ns_instances(self):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)
    
    def get_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)
   
    def delete_ns_lcm_subscriptions_subscriptionid(self, subscriptionId):
        result = {'error': True, 'data': 'Method not implemented in target MANO'}     
        return json.dumps(result)


    
    