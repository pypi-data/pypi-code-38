'''
Created on May 29, 2019

@author: KJNETHER

Code used to verify packages.
'''
import logging

import ckanapi
import pytest

from .ckan import remote_api_admin_auth
from .config_fixture import test_package_name

logger = logging.getLogger(__name__)
# pylint: disable=redefined-outer-name

# --------------------- Supporting Functions ----------------------


# need to be able to call directly... don't need to make this a fixture.
def package_delete(remote_api, test_package_name):
    '''
    :param remote_api: a ckanapi remote object
    :param pkg_name: the name of the package that needs to be deleted
    '''
    logger.debug("deleting the package: %s", test_package_name)
    remote_api.action.package_delete(id=test_package_name)


def delete_pkg(remote_api, pkg_name):
    logger.debug("checking for package: %s", pkg_name)
    pkg_exists = package_exists(remote_api, pkg_name)
    if pkg_exists:
        logger.debug("deleting package: %s", pkg_name)
        package_delete(remote_api, pkg_name)


def package_exists(remote_api, package_name, pkgtype='ANY'):
    '''
    :param remote_api: ckanapi, remote api object that is to be used to determine
                       if the package exists.
    :type remote_api: ckanapi.RemoteCKAN
    :param package_name: the package name or id who's existence is to be
                         determined
    :type package_name: str
    :param pkgtype: the package type that is to be tested for, valid values
        include:
            * ANY - tests for a package whether valid or invalid
            * VALID - tests only for valid packages
            * INVALID - tests only for invalid packages
    '''
    domain = ['ANY', 'VALID', 'INVALID']
    pkgtype = pkgtype.upper()
    if pkgtype not in domain:
        msg = 'specified an illegal pkgtype arguement, valid values include: {0}'
        msg = msg.format(','.join(domain))
        raise ValueError(msg)

    pkg_exists = False
    exists_pkg_type = 'VALID'
    try:
        pkg_data = remote_api.action.package_show(id=package_name)
        logger.debug("package show: %s", pkg_data)
        if pkg_data['name'] == package_name:
            pkg_exists = True
    except ckanapi.errors.NotFound as err:
        logger.debug("err: %s %s", type(err), err)
    except ckanapi.errors.CKANAPIError as err:
        logger.debug("err: %s %s", type(err), err)
        # assume we have a ghost package so yes say exists
        logger.debug("error assuming package exists and is invalid: %s", package_name)
        pkg_exists = True
        exists_pkg_type = 'INVALID'

    # now determine if the package was found whether we are searching for
    # a particular package type, ie valid / invalid
    if pkg_exists and pkgtype != 'ANY':
        # types don't align so the package of the specified type doesn't exist
        if pkgtype <> exists_pkg_type:
            pkg_exists = False

    return pkg_exists


# --------------------- Fixtures ----------------------
@pytest.fixture
def package_create_fixture(remote_api_admin_auth, test_pkg_data):
    '''
    :param remote_api_admin_auth: a ckanapi remote object with auth
    :param test_pkg_data: json that contains a valid object
    '''
    pkg_return = remote_api_admin_auth.action.package_create(**test_pkg_data)
    logger.debug("pkg_return: %s", pkg_return)
    yield pkg_return


@pytest.fixture
def package_create_if_not_exists(remote_api_admin_auth, test_package_name,
                                 test_valid_package_exists,
                                 test_invalid_package_exists, test_pkg_data):
    pkg_data = None
    logger.debug("test_package_exists: %s %s", test_package_exists, type(test_package_exists))
    # if a package is found that is invalid it will get deleted and a valid
    # one will be created in its place
    if test_invalid_package_exists:
        # package_delete(remote_api, test_package_name):
        package_delete(remote_api_admin_auth, test_package_name)

    if test_valid_package_exists:
        pkg_data = remote_api_admin_auth.action.package_show(id=test_package_name)
    else:
        pkg_data = remote_api_admin_auth.action.package_create(**test_pkg_data)
        logger.debug("pkg_return: %s", pkg_data)
    yield pkg_data


@pytest.fixture
def test_package_exists(remote_api_admin_auth, test_package_name):
    '''
    :param remote_api_admin_auth: a ckanapi remote object with authenticated
    :param test_package_name: the name of a package that exists
    '''
    logger.debug("testing existence of package: %s", test_package_name)
    exists = package_exists(remote_api_admin_auth, test_package_name)
    yield exists


@pytest.fixture
def test_invalid_package_exists(remote_api_admin_auth, test_package_name):
    '''
    :param remote_api_admin_auth: a ckanapi remote object with authenticated
    :param test_package_name: the name of a package that exists

    returns True if the package exists and is valid.
    '''
    logger.debug("testing if a valid package exists: %s", test_package_name)
    exists = package_exists(remote_api_admin_auth, test_package_name, 'INVALID')
    yield exists


@pytest.fixture
def test_valid_package_exists(remote_api_admin_auth, test_package_name):
    '''
    :param remote_api_admin_auth: a ckanapi remote object with authenticated
    :param test_package_name: the name of a package that exists

    returns True if the package exists and is valid.
    '''
    logger.debug("testing if a valid package exists: %s", test_package_name)
    exists = package_exists(remote_api_admin_auth, test_package_name, 'VALID')
    yield exists


@pytest.fixture
def test_pkg_teardown(remote_api_admin_auth, test_package_name, test_package_exists):
    '''
    :param remote_api_admin_auth: a ckanapi remote object with authenticated
    :type param:
    tests to see if the test package exists and removes if it does
    '''
    delete_pkg(remote_api_admin_auth, test_package_name)
    logger.debug('initial clean up complete')
    yield
    delete_pkg(remote_api_admin_auth, test_package_name)
    logger.debug('tear down cleanup complete')
