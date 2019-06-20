'''
Created on May 29, 2019

@author: KJNETHER
'''
import pytest
import ckanapi

from .load_config import ckan_url, ckan_apitoken

# pylint: disable=redefined-outer-name


@pytest.fixture
def remote_api_admin_auth(ckan_url, ckan_apitoken):
    '''
    :return: a remote ckan object with admin privs that has been authenticated
            with an api key
    :rtype: ckanapi.RemoteCKAN
    '''
    rmt_api = ckanapi.RemoteCKAN(ckan_url, ckan_apitoken)
    yield rmt_api
