from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers
from .test_nsd import *

def test_post_ns_instances_nsinstanceid_instantiate(post_ns_instances_nsinstanceid_instantiate_keys):
    """Tests API call to create a NS instance resource"""
    # Helpers._delete_test_ns_instance()
    Helpers._upload_reference_vnfd_for_nsd()
    Helpers._upload_test_nsd()
    time.sleep(5) # Wait 
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

    Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")

    assert isinstance(response, dict)
    assert set(post_ns_instances_nsinstanceid_instantiate_keys).issubset(
                    response.keys()), "All keys should be in the response"
    time.sleep(5) # Wait for NS instantiation

def test_get_ns_instances(get_ns_instances_keys):
    """Tests API call query multiple NS instances"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_ns_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
    

def test_get_ns_instances_nsinstanceid():
    """Tests API call to read an individual NS instance resource"""
    # Helpers._upload_test_ns_instance()
    # time.sleep(5) # Wait for NS instantiation
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])
    _ns = None

    for _n in _ns_list:
        if "test_osm_cirros_2vnf_nsd" == _n['nsd']['id']:            
            _ns = _n['_id']

    response = json.loads(osm_nslcm.get_ns_instances_nsinstanceid(
                        token=_token["id"], 
                        nsInstanceId=_ns))

    if response["error"]:
        return True
    else:
        return False

def test_get_vnf_instances(get_vnf_instances_keys):
    """Tests API call query multiple VNF instances"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_nslcm.get_vnf_instances(
                            token=_token["id"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_vnf_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_vnf_instances_vnfinstanceid(get_vnf_instances_vnfinstanceid_keys):
    """Tests API call to read an individual VNF instance resource"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _vnf_list = json.loads(osm_nslcm.get_vnf_instances(
                            token=_token["id"]))
    _vnf_list = json.loads(_vnf_list["data"])

    response = json.loads(osm_nslcm.get_vnf_instances_vnfinstanceid(
                            token=_token["id"], vnfInstanceId=_vnf_list[0]["id"]))

    assert response['error'] == False
    response = json.loads(response["data"])
    assert isinstance(response, dict)
    assert set(get_vnf_instances_vnfinstanceid_keys).issubset(
                response.keys()), "All keys should be in the response"



# def test_get_ns_lcm_op_ops(get_ns_lcm_op_ops_keys):
#     """Tests API call to query multiple NS LCM operation occurrences"""
#     # Helpers._upload_test_ns_instance()
#     time.sleep(5) # Wait for NS instantiation
#     osm_nslcm = OSMClient.Nslcm(HOST_URL)
#     osm_auth = OSMClient.Auth(HOST_URL)
#     _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
#     _token = json.loads(_token["data"])
#     _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
#     _ns_list = json.loads(_ns_list["data"])

#     _ns = None
#     for _n in _ns_list:
#         if "test_osm_cirros_2vnf_nsd" == _n['nsd']['id']:            
#             _ns = _n['_id']


#     response = json.loads(osm_nslcm.get_ns_lcm_op_ops(token=_token["id"], id=_ns))
#     response = json.loads(response["data"])
#     assert isinstance(response, list)
#     if len(response) > 0:
#          assert set(get_ns_lcm_op_ops_keys).issubset(
#                     response[0].keys()), "All keys should be in the response"
#     time.sleep(5)
#     # Helpers._delete_test_ns_instance()
    

# def test_get_ns_lcm_op_ops_nslcmopoccid(get_ns_lcm_op_ops_nslcmopoccid_keys):
#     """Tests API call to read an individual NS LCM operation occurrence resource"""
#     osm_nslcm = OSMClient.Nslcm(HOST_URL)
#     osm_auth = OSMClient.Auth(HOST_URL)
#     _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
#     _token = json.loads(_token["data"])
#     _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
#     _ns_list = json.loads(_ns_list["data"])

#     _ns = None
#     for _n in _ns_list:
#         if "test_osm_cirros_2vnf_nsd" == _n['nsd']['id']:            
#             _ns = _n['_id']

#     nslcmopocc = json.loads(osm_nslcm.get_ns_lcm_op_ops(token=_token["id"], id=_ns))
#     nslcmopocc = json.loads(nslcmopocc["data"])

#     _nslcmopoccid = None
#     for _nslcmopocc in nslcmopocc:
#         if "COMPLETED" or "FAILED"  == _nslcmopocc['operationState']:
#              _nslcmopoccid = _nslcmopocc['id']

#     response = json.loads(osm_nslcm.get_ns_lcm_op_ops_nslcmopoccid(
#                             token=_token["id"], 
#                             id=_nslcmopoccid))
#     response = json.loads(response["data"])
#     assert isinstance(response, dict)
#     if len(response) > 0:
#         assert set(get_ns_lcm_op_ops_nslcmopoccid_keys).issubset(
#                     response.keys()), "All keys should be in the response"
#     time.sleep(5)
#     # Helpers._delete_test_ns_instance()

def test_post_ns_instances_nsinstanceid_terminate(post_ns_instances_nsinstanceid_terminate_keys):
    """Tests API call to delete NS instance resource"""
    osm_nslcm = OSMClient.Nslcm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    _ns_list = json.loads(osm_nslcm.get_ns_instances(token=_token["id"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _ns_list:
        if "test_osm_cirros_2vnf_nsd" == _n['nsd']['id']:            
            _ns = _n['_id']
    
    response = None
    if _ns:
        response = json.loads(osm_nslcm.post_ns_instances_nsinstanceid_terminate(
                                token=_token["id"], 
                                nsInstanceId=_ns))
        _rid = response["data"]
        assert isinstance(response, dict)
        assert response["data"] == _rid

        

    




