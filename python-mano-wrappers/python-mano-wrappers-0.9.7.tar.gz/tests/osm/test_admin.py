from wrappers import OSMClient 
from pytest import fixture
from .osm_fixture import * 
from .config import *
import json
import time
from .helpers import Helpers

def test_get_user_list(get_user_list_keys):
    """Tests API call to get the list of users"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_user_list(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
         assert set(get_user_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_user_info():
    """Tests API call to get the information about individual users"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _u_list = json.loads(osm_admin.get_user_list(token=_token["id"]))
    _u_list = json.loads(_u_list["data"])

    for _u in _u_list:
        if USERNAME == _u['_id']:            
            _usr = _u['_id']

    response = json.loads(osm_admin.get_user_info(token=_token["id"], id=_usr))
    if response["error"]:
            return True
    else:
            return False

def test_get_project_list(get_project_list_keys):
    """Tests API call to get the list of projects"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_project_list(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_project_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"
    
def test_get_project_info(get_project_info_keys):
    """Tests API call to get the information about individual project"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _p_list = json.loads(osm_admin.get_project_list(token=_token["id"]))
    _p_list = json.loads(_p_list["data"])

    _project = None
    for _p in _p_list:
        if "test" == _p['_id']:            
            _project = _p['_id']

    response = json.loads(osm_admin.get_project_info(token=_token["id"], id=_project))
    if response["error"]:
            return True
    else:
            return False

def test_get_vim_list(get_vim_list_keys):
    """Tests API call to get the list of vims"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_vim_list(token=_token["id"]))
    response = json.loads(response["data"])
    assert isinstance(response, list)
    if len(response) > 0:
        assert set(get_vim_list_keys).issubset(
                    response[0].keys()), "All keys should be in the response"

def test_get_vim_info(get_vim_info_keys):
    """Tests API call to get the information about individual vim"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    _v_list = json.loads(osm_admin.get_vim_list(token=_token["id"]))
    _v_list = json.loads(_v_list["data"])

    _vim = _v_list[0]['_id']

    response = json.loads(osm_admin.get_vim_info(token=_token["id"], id=_vim))
    if response["error"]:
            return True
    else:
            return False

def test_get_sdn_list():
    """Tests API call to get the list of sdns"""
    osm_admin = OSMClient.Admin(HOST_URL)
    osm_auth = OSMClient.Auth(HOST_URL)
    _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
    _token = json.loads(_token["data"])

    response = json.loads(osm_admin.get_sdn_list(token=_token["id"]))
    response = json.loads(response["data"])
#     assert isinstance(response, list)
#     if len(response) > 0:
#         assert set(get_sdn_list).issubset(
#                     response[0].keys()), "All keys should be in the response"

# def test_get_sdn_info(get_sdn_info_keys):
#     """Tests API call to get the information about individual sdn"""
#     osm_admin = OSMClient.Admin(HOST_URL)
#     osm_auth = OSMClient.Auth(HOST_URL)
#     _token = json.loads(osm_auth.auth(username=USERNAME, password=PASSWORD))
#     _token = json.loads(_token["data"])

#     _s_list = json.loads(osm_admin.get_sdn_list(token=_token["id"]))
#     _s_list = json.loads(_s_list["data"])

#     for _s in _s_list:
#         if "admin" == _s['']:            
#             _sdn = _s['_id']

#     response = json.loads(osm_admin.get_sdn_info(token=_token["id"], id=_sdn))
#     if response["error"]:
#             return True
#     else:
#             return False




    


