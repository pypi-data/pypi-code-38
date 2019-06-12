from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import yaml
import time
from .helpers import Helpers

def test_get_son_packages(get_son_packages_keys):
    """Tests API call to fetch multiple sonata packages"""
    sonata_package = SONATAClient.Package(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(sonata_package.get_son_packages(
                                token=_token["token"]["access_token"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_son_packages_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_son_packages_PackageId(get_son_packages_PackageId_keys):
    sonata_package = SONATAClient.Package(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._upload_test_package(_token=_token["token"]["access_token"])
    _package_list = json.loads(sonata_package.get_son_packages(
                                token=_token["token"]["access_token"]))
    _package_list = json.loads(_package_list["data"])

    for _p in _package_list:
        if "sonata_example.son" == _p['grid_fs_name']:
            _package = _p['uuid']

    response = json.loads(sonata_package.get_son_packages(
                                token=_token["token"]["access_token"]))
    Helpers._delete_test_package(_token=_token["token"]["access_token"])
    if response["error"]:
        return True
    else:
        return False

def test_delete_son_packages_PackageId(delete_son_packages_PackageId_keys):
    sonata_package = SONATAClient.Package(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    
    _package_list = json.loads(sonata_package.get_son_packages(
                                token=_token["token"]["access_token"]))
    _package_list = json.loads(_package_list["data"])

    _package = None
    for _p in _package_list:
        if "sonata_example.son" == _p['grid_fs_name']:
            _package = _p['uuid']

    response = None
    if _package:
        response = json.loads(sonata_package.delete_son_packages_PackageId(
                        token=_token["token"]["access_token"], id=_package))
        assert isinstance(response, dict)
        assert response["data"] == ""

def test_post_son_packages(post_son_packages_keys):
    sonata_package = SONATAClient.Package(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    Helpers._delete_test_package(_token=_token["token"]["access_token"])

    response = json.loads(sonata_package.post_son_packages(
                        token=_token["token"]["access_token"],
                        package_path="tests/samples/sonata_example.son"))
    
    assert response['error'] == True
    assert response['data'] == ''


