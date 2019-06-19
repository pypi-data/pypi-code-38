'''
Created on May 15, 2019

@author: KJNETHER

used to verify ability to create packages:

a) create org, retrieve id
    - do round crud test or org.
b) create package with org insert the org just created for this package.

'''

import logging

import ckanapi
import pytest  # @UnusedImport
import requests

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument


def test_add_package_success(test_pkg_teardown, ckan_url, ckan_auth_header,
                             ckan_rest_dir, test_pkg_data):
    '''
    makes simple request to create package and verifies it gets
    200 status code.

    Using requests to form this call to get status code and for increased level
    of granularity over
    '''
    api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_create')
    logger.debug('api_call: %s', api_call)

    resp = requests.post(api_call, headers=ckan_auth_header, json=test_pkg_data)
    logger.debug("resp: %s", resp.text)
    assert resp.status_code == 200


def test_package_show(remote_api_admin_auth, test_package_name):
    '''
    verify package data can be retrieved using package_show.

    :param param: remote_api_admin_auth
    '''
    pkg_show_data = remote_api_admin_auth.action.package_show(id=test_package_name)
    logger.debug("pkg_show_data: %s", pkg_show_data)
    assert pkg_show_data['name'] == test_package_name


def test_package_update(remote_api_admin_auth, test_pkg_data, ckan_url,
                        ckan_rest_dir, ckan_auth_header):
    '''
    package update test will use requests
    :param remote_api_admin_auth: a ckanapi remote object with auth
    :param test_pkg_data: the package data
    :param ckan_url: ckan domain
    :param ckan_rest_dir: path to rest dir
    :param ckan_auth_header: authorization header to use in request
    '''
    test_package_name = test_pkg_data['name']
    test_pkg_data['title'] = 'zzz changed the title'
    pkg_show_data_orig = remote_api_admin_auth.action.package_show(id=test_package_name)
    # logger.debug("pkg_show_data: %s", pkg_show_data)

    api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_update')
    resp = requests.post(api_call, headers=ckan_auth_header, json=test_pkg_data)
    logger.debug("resp: %s", resp.text)
    logger.debug("resp.status_code: %s", resp.status_code)
    assert resp.status_code == 200
    # now double check that the data has been changed
    pkg_show_data = remote_api_admin_auth.action.package_show(id=test_package_name)
    assert pkg_show_data['title'] == test_pkg_data['title']
    assert pkg_show_data_orig['title'] <> pkg_show_data['title']


@pytest.mark.xfail
def test_verify_package_count(ckan_url, ckan_rest_dir, ckan_auth_header):
    '''
    verify the count reported by package_search matches packages
    returned by package_list, als seeing as a package has been
    added it should be 1 or more

    :param ckan_url: the domain portion of the ckan path
    :param ckan_rest_dir: directory path to rest calls
    :param ckan_auth_header: header struct with auth token
    '''
    # verify that the pkg_search and package_list report the same
    # total number of packages

    # using requests as can't get the limit to work with ckanapi.
    package_list_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_list')
    params = {'limit': 500, 'offset': 0}
    package_list_cnt = 0
    while True:
        logger.debug("offset: %s", params['offset'])
        resp = requests.get(package_list_call, headers=ckan_auth_header,
                            params=params)
        logger.debug("status: %s", resp.status_code)
        pkg_list = resp.json()
        package_list_cnt = package_list_cnt + len(pkg_list['result'])
        logger.debug("package cnt: %s %s", package_list_cnt,
                     len(pkg_list['result']))
        if len(pkg_list['result']) < params['limit']:
            logger.debug("end of pages, breaking out")
            break
        params['offset'] = params['limit'] + params['offset']

    logger.debug("final package cnt from packagelist: %s", package_list_cnt)

    remote_api = ckanapi.RemoteCKAN(ckan_url)
    pkg_search = remote_api.action.package_search()

    logger.debug("pkg_search cnt: %s", pkg_search['count'])
    logger.debug("pkglist cnt: %s", package_list_cnt)
    assert pkg_search['count'] == package_list_cnt
    assert len(pkg_list) >= 1


def test_package_delete(ckan_url, ckan_auth_header,
                        ckan_rest_dir, test_package_name):
    '''
    verifies that a package can actually be deleted
    '''
    api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_delete')
    logger.debug('api_call: %s', api_call)
    delete_data = {'id': test_package_name}

    resp = requests.post(api_call, headers=ckan_auth_header, json=delete_data)
    logger.debug('status code: %s', resp.status_code)
    resp_json = resp.json()
    logger.debug("resp: %s", resp.text)
    assert resp.status_code == 200
    assert resp_json['success']


# its known that this test will currently fail.  remove this decorator once this
# issue is patched
@pytest.mark.xfail
def test_package_create_invalid(test_pkg_teardown, ckan_url, ckan_auth_header,
                                ckan_rest_dir, test_pkg_data_core_only):
    '''
    CKAN Documentation suggests these are the core attributes required for a
    package:
        - name (string)
        - title (string)
        - private (bool)
        - owner_org (configurable as optional, assuming its not)

    This tests asserts that creating a package using these core attributes does
    not result in a "ghost package"

    ghost package: package_create returns 200, but subsequent package_shows
                   on same package return 500
    :param test_pkg_teardown: This fixture returns a teardown method that can be
            called multiple times to clean up package data created by this test
    :param ckan_url: url to use in construction of api calls
    :param ckan_auth_header: the auth header to use in api calls
    :param ckan_rest_dir: the directory to the api
    :param test_pkg_data_core_only: data structure that represents a test package
            that can be used in this test

    using pytest_check to provide delayed assertion
    '''
    api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_create')
    logger.debug('api_call: %s', api_call)

    resp_create = requests.post(api_call, headers=ckan_auth_header,
                                json=test_pkg_data_core_only)
    logger.debug("resp: %s", resp_create.text)
    cant_create_msg = 'Attempt to call %s returned %s'
    cant_create_msg = cant_create_msg.format(api_call,
                                             resp_create.status_code)
    assert resp_create.status_code == 200, cant_create_msg

    # now make sure the data is viewable
    api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'package_show')
    logger.debug('api_call: %s', api_call)
    resp_show = requests.post(api_call, headers=ckan_auth_header,
                              json={'id': test_pkg_data_core_only['name']})
    logger.debug('resp: %s', resp_show.text)
    non_200_msg = 'package_show on package {0} returned a status_code {1} when ' + \
                  'package_create reported {2}'

    non_200_msg = non_200_msg.format(test_pkg_data_core_only['name'],
                                     resp_show.status_code,
                                     non_200_msg)
    assert resp_show.status_code == 200, non_200_msg

    logger.debug("resp text: %s", resp_show.text)
    logger.debug("tear down has been called")
