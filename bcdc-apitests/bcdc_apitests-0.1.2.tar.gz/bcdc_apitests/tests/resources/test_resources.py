'''
Created on Jun. 11, 2019

@author: crigdon
'''

import logging
import requests
import ckanapi

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


# looks like a resource has to be part of a package, ie the package_id needs to
# be populated.  Call the fixtures
def test_resource_create(ckan_url, ckan_rest_dir, ckan_auth_header,
                         resource_data,package_create_fixture,package_create_if_not_exists):
    '''
    add new resource

    :param ckan_url: domain to be used for ckan calls
    :param ckan_rest_dir: root path to the rest api
    :param ckan_auth_header: authorization header
    :param resource_data: the resource data to be used in the creation of a
        new resource object
    :param package_create_if_not_exists: create pkg if it does not exist
    '''

    #return pkg
    pkg = package_create_if_not_exists
    #pkg = package_create_fixture
    logger.debug("package_create id is: %s", pkg['id'])

    try:
        # define api call
        api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'resource_create')
        logger.debug('api_call: %s', api_call)

        # get pkg id
        resource_data['package_id'] = pkg['id']

        # create resource
        res_data = requests.post(api_call, headers=ckan_auth_header, json=resource_data)
        logger.debug("resource_create: %s", res_data.text)

        # get resource id
        resp_json = res_data.json()
        resId = resp_json['result']['id']

        assert res_data.status_code == 200

        # check is resource exist
        # define remote api
        api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'resource_show')
        logger.debug('api_call: %s', api_call)
        res_data = requests.post(api_call, headers=ckan_auth_header, json={'id': resId})
        logger.debug("resource_show: %s", res_data.text)

        resp_json = res_data.json()

        assert resp_json['success']

    except ckanapi.CKANAPIError as err:
        logger.debug("err: %s %s", type(err), err)
        raise err


# update resource
def test_resource_update(remote_api_admin_auth,ckan_url,ckan_rest_dir,ckan_auth_header,resource_data):
    '''
    :param remote_api_admin_auth: ckanapi remote, with auth
    :param resource_data: test resource structure
    :param ckan_url:
    :param ckan_rest_dir:
    :param ckan_auth_header:
    '''
    try:

        # define remote api
        remote_api = remote_api_admin_auth
        logger.debug("resource_name: %s", resource_data['name'])

        # using search to get the ID of resource.
        res_data = remote_api.action.resource_search(query="name:{0}".format(resource_data['name']))
        logger.debug("resource_data: %s", res_data)

        # update resource data dic with package id
        resource_data['package_id'] = res_data['results'][0]['package_id']
        logger.debug("resource_pkgID: %s", resource_data['package_id'])

        # add id key to resource data dic
        resource_data['id'] = res_data['results'][0]['id']
        logger.debug("resource_id: %s", resource_data['id'])

        # change some data in resource data dic
        resource_data['description'] = 'test resource description changed'

        # define api
        api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'resource_update')
        logger.debug('api_call: %s', api_call)

        # update resource
        res_data = requests.post(api_call, headers=ckan_auth_header, json=resource_data)
        logger.debug("resource_update: %s", res_data.text)

        assert res_data.status_code == 200

    except ckanapi.CKANAPIError as err:
        logger.debug("err: %s %s", type(err), err)


# search resource
def test_resource_search(remote_api_admin_auth, resource_data):
    '''
    :param remote_api_admin_auth: ckanapi remote, with auth
    :param resource_data: test resource structure
    '''
    try:
        # define remote api
        remote_api = remote_api_admin_auth
        logger.debug("resource_name: %s", resource_data['name'])

        # search for resource by name
        res_data = remote_api.action.resource_search(query="name:{0}".format(resource_data['name']))
        logger.debug("resource search: %s", res_data)

        assert res_data['count'] >= 1

    except ckanapi.CKANAPIError as err:
        logger.debug("err: %s %s", type(err), err)


# delete resource
def test_resource_delete(remote_api_admin_auth,ckan_url,ckan_rest_dir,ckan_auth_header, resource_data):
    '''
    :param remote_api_admin_auth: ckanapi remote, with auth
    :param resource_data: test resource structure
    '''
    try:
        # define api
        remote_api = remote_api_admin_auth

        # search to get the ID of resource.
        res_data = remote_api.action.resource_search(query="name:{0}".format(resource_data['name']))
        resID = res_data['results'][0]['id']

        # delete resource by id
        res_data = remote_api.action.resource_delete(id=resID)
        logger.debug("resource_delete: %s", res_data)

        # check is resource exist
        # define api
        api_call = '{0}{1}/{2}'.format(ckan_url, ckan_rest_dir, 'resource_show')
        logger.debug('api_call: %s', api_call)

        # show resource
        res_data = requests.post(api_call, headers=ckan_auth_header, json={'id': resID})
        logger.debug("resource_show: %s", res_data.text)

        resp_json = res_data.json()
        assert not resp_json['success']

    except ckanapi.CKANAPIError as err:
        logger.debug("err: %s %s", type(err), err)


# remove test package
# TODO: move this into a fixture, thinking could configure a fixture in the conftest
#       with a module scope that does the package creation and deletion.
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