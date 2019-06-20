'''
Created on May 13, 2019

@author: KJNETHER

trying to set up the fixtures so that they:
- test for 'test' data
- remove 'test' data if it already exists
- re-create test data

'''
import json
import logging
import os.path

import pytest

# pylint: disable=redefined-outer-name

from .config_fixture import test_package_name
from .config_fixture import test_user

logger = logging.getLogger(__name__)

@pytest.fixture
def test_data_dir():
    '''
    :return: the data directory
    '''
    pkg_json_dir = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    yield pkg_json_dir


@pytest.fixture
def test_pkg_data(test_data_dir, test_package_name, test_user):
    '''
    :param test_data_dir: the data directory fixture, provides the directory
                          where data is located
    :param test_package_name: the name of the test package
    '''
    logger.debug("test_package_name: %s", test_package_name)
    logger.debug("test user: %s", test_user)
    json_file = os.path.join(test_data_dir, 'pkgData_min.json')
    with open(json_file, 'r') as json_file_hand:
        datastore = json.load(json_file_hand)
        datastore['name'] = test_package_name
        datastore['title'] = '{0} {1}'.format(datastore['title'], test_user)
    return datastore


@pytest.fixture
def resource_data(test_data_dir, test_resource_name):
    '''
    :param test_data_dir: The directory where the data files are
        expected to be
    :param test_resource_name: the name of the resource that should
        be used for this test
    '''
    logging.debug("test_package_name: %s", test_package_name)
    json_file = os.path.join(test_data_dir, 'resource.json')
    with open(json_file, 'r') as json_file_hand:
        datastore = json.load(json_file_hand)
        datastore['name'] = test_resource_name
    return datastore


@pytest.fixture
def test_pkg_data_core_only(test_pkg_data):
    '''
    :param test_pkg_data: Valid package data

    Method will remove all but the core attributes required as described in
    the ckan docs.

    (https://docs.ckan.org/en/2.8/api/#module-ckan.logic.action.create)

    core attributes:
        - name (string)
        - title (string)
        - private (bool)
        - owner_org (configurable as optional, assuming its not)
    '''
    logging.debug("test_package_name: %s", test_pkg_data)
    core_attribs = ['name', 'title', 'private', 'owner_org']
    core_atribs_only_pkg = {}
    for key in test_pkg_data.keys():
        if key in core_attribs:
            core_atribs_only_pkg[key] = test_pkg_data[key]
    return core_atribs_only_pkg


@pytest.fixture
def test_pkg_data_updated(test_pkg_data):
    '''
    :param test_pkg_data: package data structure that can be used to load a new
                          package
    '''
    logging.debug("test_package_name: %s", test_package_name)
    test_pkg_data['title'] = 'test package update'
    return test_pkg_data


@pytest.fixture
def test_org_data(test_data_dir, test_organization):
    '''
    :return:  an organization data structure that can be used for testing
    '''
    json_file = os.path.join(test_data_dir, 'ownerOrg.json')
    with open(json_file, 'r') as json_file_hand:
        org_data = json.load(json_file_hand)
        org_data['name'] = test_organization
    return org_data
