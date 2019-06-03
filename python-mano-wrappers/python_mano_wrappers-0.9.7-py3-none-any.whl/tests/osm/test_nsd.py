from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers

def test_post_ns_descriptors(post_ns_descriptors_keys):
    """Tests API call to onboard NS descriptor resources"""
    Helpers._delete_test_nsd()
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

    assert isinstance(response, dict)
    assert set(post_ns_descriptors_keys).issubset(
                    response.keys()), "All keys should be in the response"

def test_get_ns_descriptors(get_ns_descriptors_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    osm_nsd = OSMClient.Nsd(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_ns_descriptors_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_delete_ns_descriptors_nsdinfoid(delete_ns_descriptors_nsdinfoid_keys):
    """Tests API call to delete NS descriptor resources"""
    osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
    osm_nsd = OSMClient.Nsd(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
    _nsd_list = json.loads(_nsd_list["data"])

    _nsd = None
    for _n in _nsd_list:
        if "test_osm_cirros_2vnf_nsd" == _n['id']:            
            _nsd = _n['_id']

    time.sleep(10) # Wait for NSD onboarding
    response = json.loads(osm_nsd.delete_ns_descriptors_nsdinfoid(
                                token=_token["id"], 
                                nsdinfoid=_nsd))

    time.sleep(2) # Wait for NSD onboarding

    _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']

    response = None
    if _vnfd:
        response = json.loads(osm_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                token=_token["id"], 
                                vnfPkgId=_vnfd))
        assert isinstance(response, dict)
        assert response["data"] == ""

    assert isinstance(response, dict)
    assert response["data"] == ""

def test_get_ns_descriptors_nsd_content():
    """Tests API call to fetch the content of a NSD"""
    osm_nsd = OSMClient.Nsd(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_nsd()
    _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
    _nsd_list = json.loads(_nsd_list["data"])

    for _n in _nsd_list:
        if "test_osm_cirros_2vnf_nsd" == _n['id']:            
            _nsd = _n['_id']

    response = json.loads(osm_nsd.get_ns_descriptors_nsd_content(
                                token=_token["id"], 
                                nsdinfoid=_nsd))
    Helpers._delete_test_nsd()
    if response["error"]:
            return True
    else:
            return False

def test_put_ns_descriptors_nsd_content():
    """Tests API call to upload the content of a NSD"""
    osm_nsd = OSMClient.Nsd(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_reference_vnfd_for_nsd()
    Helpers._upload_test_nsd()
    _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
    _nsd_list = json.loads(_nsd_list["data"])

    _nsd = None
    for _n in _nsd_list:
        if "test_osm_cirros_2vnf_nsd" == _n['id']:            
            _nsd = _n['_id']

    response = json.loads(osm_nsd.put_ns_descriptors_nsd_content(
                        token=_token["id"], 
                        nsdinfoid=_nsd, 
                        data_path="tests/samples/test_osm_cirros_nsd.tar.gz" ))
    Helpers._delete_test_nsd("test_osm_cirros_2vnf_nsd")
    if response["error"]:
            return True
    else:
            return False

def test_get_ns_descriptors_nsdinfoid():
    """Tests API call to read information about an individual NS descriptor resource"""
    osm_nsd = OSMClient.Nsd(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_nsd()
    _nsd_list = json.loads(osm_nsd.get_ns_descriptors(token=_token["id"]))
    _nsd_list = json.loads(_nsd_list["data"])

    for _n in _nsd_list:
        if "test_osm_cirros_2vnf_nsd" == _n['id']:            
            _nsd = _n['_id']

    response = json.loads(osm_nsd.get_ns_descriptors_nsdinfoid(token=_token["id"], nsdinfoid=_nsd))
    Helpers._delete_test_nsd()
    if response["error"]:
        return True
    else:
        return False

