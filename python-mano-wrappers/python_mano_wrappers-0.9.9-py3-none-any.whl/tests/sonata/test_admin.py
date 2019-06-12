from wrappers import SONATAClient 
from pytest import fixture
from .sonata_fixture import * 
from .config import *
import json
import time
# from .helpers import Helpers

def test_get_user_list(get_user_list_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_admin.get_user_list(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])

    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_user_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_user_info(get_user_info_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _u_list = json.loads(sonata_admin.get_user_list(token=_token["token"]["access_token"]))
    _u_list = json.loads(_u_list["data"])

    for _u in _u_list:
        if "Admin" == _u['first_name']:            
            _usr = _u['uuid']

    response = json.loads(sonata_admin.get_user_info(token=_token["token"]["access_token"], id=_usr))
    if response["error"]:
            return True
    else:
            return False

def test_get_nsinstances_records(get_nsinstances_records_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_admin.get_nsinstances_records(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])
    
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_nsinstances_records_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_nsinstances_records_instanceId(get_nsinstances_records_instanceId_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _nsr_list = json.loads(sonata_admin.get_nsinstances_records(token=_token["token"]["access_token"]))
    _nsr_list = json.loads(_nsr_list["data"])
    
    for _n in _nsr_list:
        if "nsr-schema-01" == _n['descriptor_version']:         
            _nsr = _n['uuid']

    response = json.loads(sonata_admin.get_nsinstances_records_instanceId(token=_token["token"]["access_token"], id=_nsr))
    if response["error"]:
            return True
    else:
            return False

def test_get_vims_list(get_vims_list_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_admin.get_vims_list(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])
    
    assert isinstance(response, dict)
    if len(response) > 0:
         assert set(get_vims_list_keys).issubset(
                    response.keys()), "All keys should be in the response"


def test_get_instantions_requests(get_instantions_requests_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_admin.get_instantions_requests(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])
    
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_instantions_requests_keys).issubset(
                    response[0].keys()), "All keys should be in the response"


def test_get_instantions_requests_requestId(get_instantions_requests_requestId_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _r_list = json.loads(sonata_admin.get_instantions_requests(token=_token["token"]["access_token"]))
    _r_list = json.loads(_r_list["data"])

    for _r in _r_list:
        if "http://son-gtkkpi:5400/service-instantiation-time" == _r['callback']:            
            _ir = _r['id']

    response = json.loads(sonata_admin.get_instantions_requests_requestId(token=_token["token"]["access_token"], id=_ir))
    if response["error"]:
            return True
    else:
            return False

def test_get_functions(get_functions_keys): 
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])
    response = json.loads(sonata_admin.get_functions(token=_token["token"]["access_token"]))
    response = json.loads(response["data"])
    
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_functions_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
 

def test_get_functions_functionId(get_functions_functionId_keys):
    time.sleep(2) #Wait 
    sonata_admin = SONATAClient.Admin(HOST_URL)
    sonata_auth = SONATAClient.Auth(HOST_URL)
    _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _f_list = json.loads(sonata_admin.get_functions(token=_token["token"]["access_token"]))
    _f_list = json.loads(_f_list["data"])

    for _f in _f_list:
        if "dummy-vnf" == _f['vnfd']['name']:            
            _fun = _f['uuid']

    response = json.loads(sonata_admin.get_functions_functionId(token=_token["token"]["access_token"], id=_fun))
  
# def test_get_packages(get_packages_keys):
#     sonata_admin = SONATAClient.Admin(HOST_URL)
#     sonata_auth = SONATAClient.Auth(HOST_URL)
#     _token = json.loads(sonata_auth.auth(username=USERNAME, password=PASSWORD))
#     _token = json.loads(_token["data"])
#     response = json.loads(sonata_admin.get_packages(token=_token["token"]["access_token"]))
#     response = json.loads(response["data"])
    
#     assert isinstance(response, list)
#     if len(response) > 0:
#          assert set(get_packages_keys).issubset(
#                     response[0].keys()), "All keys should be in the response"

