'''
Created on May 27, 2019

@author: KJNETHER

putting global configuration parameters into this file

'''

import pytest
import getpass

# getting first three letters of username
TEST_USER = getpass.getuser()[0:3].lower()

# Following are test constants
TEST_PREFIX = 'zzztest'
# TEST_ORGANIZATION = '{0}_testorg'.format(TEST_PREFIX)
# TODO: need to modify to use the testing org that should be set up.
TEST_ORGANIZATION = 'databc'
TEST_PACKAGE = '{0}_{1}_testpkg'.format(TEST_PREFIX, TEST_USER)
TEST_RESOURCE = '{0}_{1}_testresource'.format(TEST_PREFIX, TEST_USER)
BCDC_REST_DIR = "/api/3/action"

# pylint: disable=redefined-outer-name


@pytest.fixture
def test_user():
    '''
    :return: the test user letters to be appended to test objects to keep them
        unique between testers
    '''
    return TEST_USER


@pytest.fixture
def test_prefix():
    '''
    :return: the test object naming prefix
    '''
    return TEST_PREFIX


@pytest.fixture
def test_organization():
    '''
    :return: the name of the organization that should be owned by tests
    '''
    return TEST_ORGANIZATION


@pytest.fixture
def test_package_name():
    '''
    :return: the name of the package to be used for the testing.
    '''
    return TEST_PACKAGE


@pytest.fixture
def test_resource_name():
    '''
    :return: the name of the package to be used for the testing.
    '''
    return TEST_RESOURCE


@pytest.fixture
def ckan_rest_dir():
    '''
    :return: the ckan rest dir.
    '''
    return BCDC_REST_DIR
