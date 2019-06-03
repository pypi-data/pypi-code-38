import json
from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
from .helpers import Helpers

def test_post_vnf_packages(post_vnf_packages_keys):
    """Tests API call to onboard VNF descriptor resources"""
    Helpers._delete_test_nsd()
    Helpers._delete_test_vnf()
    osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_vnfpkgm.post_vnf_packages(token=_token["id"],
                        package_path="tests/samples/test_osm_cirros_vnfd.tar.gz"))
    response = json.loads(response["data"])
    
    assert isinstance(response, dict)
    assert set(post_vnf_packages_keys).issubset(
                    response.keys()), "All keys should be in the response"
    

def test_get_vnf_packages(get_vnf_packages_keys):
    """Tests API call to fetch multiple NS descriptor resources"""
    osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_vnf_packages_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_vnf_packages_vnfpkgid(get_vnf_packages_vnfpkgid_keys):
    """Tests API call to onboard VNF descriptor resources"""
    osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _vnfd_list = json.loads(osm_vnfpkgm.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    for _v in _vnfd_list:
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']

    response = json.loads(osm_vnfpkgm.get_vnf_packages_vnfpkgid(
                                token=_token["id"], 
                                vnfPkgId=_vnfd))

def test_delete_vnf_packages_vnfpkgid(delete_vnf_packages_vnfpkgid_keys):
    """Tests API call to delete NS descriptor resources"""
    osm_vnfpkgm = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_vnf()
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

def test_get_vnf_packages_vnfpkgid_vnfd():
    """Tests API call to read VNFD of an onboarded VNF package"""
    osm_vnfpkgm_vnfd = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_vnf()
    _vnfd_list = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    for _v in _vnfd_list:
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']

    response = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages_vnfpkgid_vnfd(
                        token=_token["id"], 
                        vnfPkgId=_vnfd))
    Helpers._delete_test_vnf()
    if response["error"]:
            return True
    else:
            return False

def test_get_vnf_packages_vnfpkgid_package_content():
    """Tests API call to fetch an onboarded VNF package"""
    osm_vnfpkgm_vnfd = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_vnf()
    _vnfd_list = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    for _v in _vnfd_list:
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']

    response = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages_vnfpkgid_package_content(
                                token=_token["id"], 
                                vnfPkgId=_vnfd))
    Helpers._delete_test_vnf()
    if response["error"]:
            return True
    else:
            return False

def test_get_vnf_packages_vnfpkgid_artifacts_artifactpath():
    """Tests API call to fetch an onboarded VNF package"""
    osm_vnfpkgm_vnfd = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_vnf()
    _vnfd_list = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    for _v in _vnfd_list:
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']

    response = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages_vnfpkgid_artifacts_artifactpath(
                                token=_token["id"], 
                                vnfPkgId=_vnfd))
    Helpers._delete_test_vnf()
    if response["error"]:
            return True
    else:
            return False

def test_put_vnf_packages_vnfpkgid_package_content():
    """Tests API call to Upload a VNF package by
    providing the content of the VNF
    package"""
    osm_vnfpkgm_vnfd = OSMClient.VnfPkgm(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_vnf()
    _vnfd_list = json.loads(osm_vnfpkgm_vnfd.get_vnf_packages(token=_token["id"]))
    _vnfd_list = json.loads(_vnfd_list["data"])
    
    _vnfd = None
    for _v in _vnfd_list: 
        if "test_osm_cirros_vnfd" == _v['id']:            
            _vnfd = _v['_id']
           
    response = json.loads(osm_vnfpkgm_vnfd.put_vnf_packages_vnfpkgid_package_content(
                                token=_token["id"], vnfPkgId=_vnfd,
                                data_path="tests/samples/test_osm_cirros_vnfd.tar.gz"))
    Helpers._delete_test_vnf("test_osm_cirros_2vnf_nsd")
    if response["error"]:
            return True
    else:
            return False


    
   
   





    