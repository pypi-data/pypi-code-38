# coding=utf-8

import json
import pytest
import responses
from ibm_ai_openscale_cli.setup_classes.cloud_foundry import CloudFoundry


base_url = 'https://api.ng.bluemix.net'
USER_INFO_URL = 'https://uaa.ng.bluemix.net/userinfo'

fake_access_token = 'foo_token'

fake_result = {
    'metadata': {
        'guid': '9881c79e-d269-4a53-9d77-cb21b745356e',
        'created_at': '2016-06-08T16:41:37Z'
    },
    'entity': {
        'name': 'foo',
        'organization_guid': '9881c79e-d269-4a53-9d77-cb21b745356e',
        'space_guid': '9881c79e-d269-4a53-9d77-cb21b745356e',
        'service_guid': '3ab19880-ab42-4d0e-a229-ac93fc02beb4',
        'credentials': {
            'creds-key-7': 'creds-val-7'
        }
    }
}

fake_results = {
    'total_results': 1,
    'resources': [fake_result]
}

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_create_instance_key():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/service_keys'.format(base_url)
    request_data = {
        'service_instance_guid': 'foo',
        'name': 'openscale-fastpath-credentials'
    }
    responses.add(
        responses.POST,
        url,
        body=json.dumps(fake_result),
        status=201,
        content_type='application/json')

    response = cf.create_instance_key(service_instance_guid='foo')

    assert len(responses.calls) == 1
    responses.calls[0].request.body = request_data
    assert response == fake_result

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_list_spaces():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/users/{1}/spaces'.format(base_url, 'user-foo')
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.list_spaces(user_id='user-foo')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources']
    assert responses.calls[0].request.body is None

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_list_organizations():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/users/{1}/organizations'.format(base_url, 'user-foo')
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.list_organizations(user_id='user-foo')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources']
    assert responses.calls[0].request.body is None

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_list_plans_by_service():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/services/{1}/service_plans'.format(base_url, 'service-guid')
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.list_plans_by_service(service_guid='service-guid')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources']
    assert responses.calls[0].request.body is None

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_list_instance_keys():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/service_instances/{1}/service_keys'.format(
        base_url, 'guid-foo')
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.list_instance_keys(guid='guid-foo')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources']

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_get_service_by_name():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/services?q=label%3Amessi'.format(base_url)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.get_service_by_name(name='messi')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources'][0]

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_list_instances_by_plan():
    cf = CloudFoundry(access_token=fake_access_token)
    query = 'q=space_guid+IN+{0}%2C{0}%2C{0}'.format(
        fake_result['metadata']['guid'])
    url = '{0}/v2/service_plans/{1}/service_instances?{2}'.format(
        base_url, 'free', query)
    responses.add(
        responses.GET,
        url,
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.list_instances_by_plan(
        plan='free', spaces=[fake_result, fake_result, fake_result])

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == url
    assert response == fake_results['resources']

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_delete_instance_key():
    cf = CloudFoundry(access_token=fake_access_token)
    guid = '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8'
    url = '{0}/v2/resource_keys/{1}'.format(base_url, guid)
    responses.add(
        responses.DELETE,
        url,
        body='',
        status=200)

    cf.delete_instance_key(guid=guid)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_create_instance():
    cf = CloudFoundry(access_token=fake_access_token)
    url = '{0}/v2/service_instances?accepts_incomplete=false'.format(base_url)
    responses.add(responses.POST,
                  url,
                  body=json.dumps(
                      fake_result),
                  status=201,
                  content_type='application/json')

    response = cf.create_instance(
        name='name',
        service_plan_guid='service_plan_guid',
        space_guid='space_guid')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert response == fake_result

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_delete_instance():
    cf = CloudFoundry(access_token=fake_access_token)
    resource_id = '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8'
    url = '{0}/v2/service_instances/{1}'.format(base_url, resource_id)
    responses.add(
        responses.DELETE,
        url,
        body='',
        status=200)

    cf.delete_instance(guid=resource_id)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert 'accepts_incomplete=false' in responses.calls[0].request.url
    assert 'recursive=true' in responses.calls[0].request.url

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_get_or_create_instance_without_org_and_space():
    cf = CloudFoundry(access_token=fake_access_token)
    user_id = 'maradona'
    fake_guid = fake_result['metadata']['guid']
    service_name = 'conversation'

    responses.add(
        responses.GET,
        USER_INFO_URL,
        body=json.dumps({'user_id': user_id}),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/users/{1}/organizations'.format(base_url, user_id),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/users/{1}/spaces'.format(base_url, user_id),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')
    # list instance

    responses.add(
        responses.GET,
        '{0}/v2/service_plans/{1}/service_instances?q=space_guid+IN+{1}'.format(
            base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/services?q=label%3A{1}'.format(base_url, service_name),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/services/{1}/service_plans'.format(base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(responses.POST,
                  '{0}/v2/service_instances?accepts_incomplete=false'.format(
                      base_url),
                  body=json.dumps(
                      fake_result),
                  status=201,
                  content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/service_instances/{1}/service_keys'.format(
            base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.get_or_create_instance(
        service_name='conversation',
        service_plan_guid='service_plan_guid')

    assert len(responses.calls) == 7
    assert response['id'] == fake_guid
    assert response['created_at'] == fake_result['metadata']['created_at']
    assert response['credentials'] == fake_result['entity']['credentials']

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@responses.activate
def test_get_or_create_instance_with_org_and_space():
    cf = CloudFoundry(access_token=fake_access_token)
    user_id = 'maradona'
    fake_guid = fake_result['metadata']['guid']
    service_name = 'conversation'

    responses.add(
        responses.GET,
        USER_INFO_URL,
        body=json.dumps({'user_id': user_id}),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/users/{1}/organizations'.format(base_url, user_id),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/users/{1}/spaces'.format(base_url, user_id),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')
    # list instance

    responses.add(
        responses.GET,
        '{0}/v2/service_plans/{1}/service_instances?q=space_guid+IN+{1}'.format(
            base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/services?q=label%3A{1}'.format(base_url, service_name),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/services/{1}/service_plans'.format(base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    responses.add(responses.POST,
                  '{0}/v2/service_instances?accepts_incomplete=false'.format(
                      base_url),
                  body=json.dumps(
                      fake_result),
                  status=201,
                  content_type='application/json')

    responses.add(
        responses.GET,
        '{0}/v2/service_instances/{1}/service_keys'.format(
            base_url, fake_guid),
        body=json.dumps(fake_results),
        status=200,
        content_type='application/json')

    response = cf.get_or_create_instance(
        service_name='conversation',
        service_plan_guid='service_plan_guid',
        organization_name='foo',
        space_name='foo')

    assert len(responses.calls) == 7
    assert response['id'] == fake_guid
    assert response['created_at'] == fake_result['metadata']['created_at']
    assert response['credentials'] == fake_result['entity']['credentials']
