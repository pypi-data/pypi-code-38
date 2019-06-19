'''
Created on May 16, 2019

@author: KJNETHER

Can't test orgs as there is no way to create orgs without superuser


'''
import logging

import ckanapi
import pytest

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def test_verify_read_orgs(ckan_url):
    '''
    verifies can retrieve a list of organizations and that there is at least
    one org defined
    '''
    remote_api = ckanapi.RemoteCKAN(ckan_url)
    pkg_list = remote_api.action.organization_list()
    logger.debug("orglist cnt: %s", len(pkg_list))
    assert pkg_list


def test_verify_test_org_exists(ckan_url, ckan_apitoken, test_organization):
    '''
    verifies that the test_organization exists
    '''
    org = ''
    remote_api = ckanapi.RemoteCKAN(ckan_url, ckan_apitoken)
    try:
        org = remote_api.action.organization_show(id=test_organization)
    except ckanapi.errors.NotFound as err:
        msg = 'The test organization {0} that is required for most tests does ' + \
              'not exist'
        logger.debug("error: %s", type(err))
        msg = msg.format(test_organization)
        logger.error(msg)
        pytest.fail(msg)
    logger.debug("org: %s", org)

# LEAVING COMMENTED OUT FOR NOW UNTIL WE DETERMINE WHETHER THE TESTS WILL BE
# RUN AS SUPER ADMIN OR AS ADMIN WITH PRECONFIGURED ORGS
# def test_add_organization(test_org_data, ckan_url, ckan_apitoken):
#     '''
#     Cannot create the create orgs without superuser at the moment so this
#     test will remain commented out until that is resolved.
#     '''
#     remoteApi = ckanapi.RemoteCKAN(ckan_url, ckan_apitoken)
#
#     # orgList = remoteApi.action.organization_list_for_user()
#     # logger.debug("orgList: %s", orgList)
#     # pkg_create = remoteApi.action.organization_create(**test_org_data)
#     # logger.debug("org return data: %s", pkg_create)
#     logger.warning('not running org creation tests')
