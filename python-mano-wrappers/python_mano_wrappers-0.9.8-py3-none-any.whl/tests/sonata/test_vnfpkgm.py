import json
import yaml
import time
from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
from .helpers import Helpers

def test_post_vnf_packages(post_vnf_packages_keys):
	"""Tests API call to onboard VNF descriptor resources"""
	sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
	sonata_auth = SONATAClient.Auth(HOST_URL)

	_token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
	_token = json.loads(_token["data"])
	Helpers._delete_test_vnf(_token=_token["token"]["access_token"])

	response = json.loads(sonata_vnfpkgm.post_vnf_packages(
                                token=_token["token"]["access_token"],
                                package_path="tests/samples/vnfd_example.yml"))

	assert response['error'] == True
	assert response['data'] != ''
    

def test_get_vnf_packages(get_vnf_packages_keys):
	"""Tests API call to fetch multiple NS descriptor resources"""
	sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
	sonata_auth = SONATAClient.Auth(HOST_URL)
	_token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
	_token = json.loads(_token["data"])
	
	response = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
	
	response = json.loads(response["data"])
	assert isinstance(response, list)
	if len(response) > 0:
		assert set(get_vnf_packages_keys).issubset(
					response[0].keys()), "All keys should be in the response"


def test_delete_vnf_packages_vnfpkgid(delete_vnf_packages_vnfpkgid_keys):
    """Tests API call to delete NS descriptor resources"""
    sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "vnfd_example" == _v['uuid']:            
            _vnfd = _v['uuid']

    response = None
    if _vnfd:
        response = json.loads(sonata_vnfpkgm.delete_vnf_packages_vnfpkgid(
                                        token=_token["token"]["access_token"],
                                        vnfPkgId=_vnfd))
        assert isinstance(response, dict)
        assert response["data"] == ""

def test_get_vnf_packages_vnfpkgid(get_vnf_packages_vnfpkgid_keys):
    """Tests API call to onboard VNF descriptor resources"""
    sonata_vnfpkgm = SONATAClient.VnfPkgm(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _vnfd_list = json.loads(sonata_vnfpkgm.get_vnf_packages(token=_token["token"]["access_token"]))
    _vnfd_list = json.loads(_vnfd_list["data"])

    _vnfd = None
    for _v in _vnfd_list:
        if "vnfd_example" == _v['uuid']:            
            _vnfd = _v['uuid']

    response = json.loads(sonata_vnfpkgm.get_vnf_packages_vnfpkgid(
                                token=_token["token"]["access_token"], 
                                vnfPkgId=_vnfd))