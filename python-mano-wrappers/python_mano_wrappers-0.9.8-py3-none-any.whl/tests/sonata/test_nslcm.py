from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers


def test_get_ns_instances(get_ns_instances_keys):
    """Tests API call query multiple NS instances"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_nslcm.get_ns_instances(
                            token=_token["token"]["access_token"], limit=1000))
    response = json.loads(response["data"])
    print(len(response))
    print(response)
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_ns_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_ns_instances_nsinstanceid(test_get_ns_instances_nsinstanceid_keys):
    """Tests API call to read an individual NS instance resource"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    sonata_nsd = SONATAClient.Nsd(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
                            token=_token["token"]["access_token"]))
    _nsd_list = json.loads(_nsd_list["data"])

    _ns_list = json.loads(sonata_nslcm.get_ns_instances(
                            token=_token["token"]["access_token"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _nsd_list:
        if "A dummy Example." == _n['nsd']['description']:
            for _n2 in _ns_list:
                if _n['uuid'] == _n2['descriptor_reference']:
                    _ns = _n2['uuid']

    response = json.loads(sonata_nslcm.get_ns_instances_nsinstanceid(
                            token=_token["token"]["access_token"], nsInstanceId=_ns))

    print(response)
    assert response['error'] == False
    response = json.loads(response["data"])
    assert isinstance(response, dict)
    assert set(test_get_ns_instances_nsinstanceid_keys).issubset(
                response.keys()), "All keys should be in the response"


def test_get_vnf_instances(get_vnf_instances_keys):
    """Tests API call query multiple VNF instances"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_nslcm.get_vnf_instances(
                            token=_token["token"]["access_token"], limit=1000))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_vnf_instances_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_vnf_instances_vnfinstanceid(get_vnf_instances_vnfinstanceid_keys):
    """Tests API call to read an individual VNF instance resource"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _vnf_list = json.loads(sonata_nslcm.get_vnf_instances(
                            token=_token["token"]["access_token"]))
    _vnf_list = json.loads(_vnf_list["data"])

    response = json.loads(sonata_nslcm.get_vnf_instances_vnfinstanceid(
                            token=_token["token"]["access_token"], vnfInstanceId=_vnf_list[0]["uuid"]))

    assert response['error'] == False
    response = json.loads(response["data"])
    assert isinstance(response, dict)
    assert set(get_vnf_instances_vnfinstanceid_keys).issubset(
                response.keys()), "All keys should be in the response"


def test_post_ns_instances_nsinstanceid_instantiate(post_ns_instances_nsinstanceid_instantiate_keys):
    """Tests API call to instantiate an NS"""
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

        assert response['error'] == False
        response = json.loads(response["data"])
        assert isinstance(response, dict)
        assert set(post_ns_instances_nsinstanceid_instantiate_keys).issubset(
                    response.keys()), "All keys should be in the response"
    else:
        return False

def test_post_ns_instances_nsinstanceid_terminate(post_ns_instances_nsinstanceid_terminate_keys):
    """Tests API call to instantiate an NS"""
    sonata_nslcm = SONATAClient.Nslcm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    sonata_nsd = SONATAClient.Nsd(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _nsd_list = json.loads(sonata_nsd.get_ns_descriptors(
                            token=_token["token"]["access_token"]))
    _nsd_list = json.loads(_nsd_list["data"])

    _ns_list = json.loads(sonata_nslcm.get_ns_instances(
                            token=_token["token"]["access_token"]))
    _ns_list = json.loads(_ns_list["data"])

    _ns = None
    for _n in _nsd_list:
        if "A dummy Example." == _n['nsd']['description']:
            for _n2 in _ns_list:
                if _n['uuid'] == _n2['descriptor_reference']:
                    _ns = _n2['uuid']

    if _ns:
        response = json.loads(
                    sonata_nslcm.post_ns_instances_nsinstanceid_terminate(
                        token=_token["token"]["access_token"], nsInstanceId=_ns))

        assert response['error'] == False
        response = json.loads(response["data"])
        assert isinstance(response, dict)
        assert set(post_ns_instances_nsinstanceid_terminate_keys).issubset(
                    response.keys()), "All keys should be in the response"
    else:
        return False

                





