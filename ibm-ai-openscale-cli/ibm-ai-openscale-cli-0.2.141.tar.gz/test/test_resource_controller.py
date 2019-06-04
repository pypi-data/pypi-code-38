# coding=utf-8

import json
import responses
from ibm_ai_openscale_cli.setup_classes.resource_controller import ResourceController

base_url = 'https://resource-controller.bluemix.net'
fake_access_token = 'foo_token'

fake_instance = {
    'id': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
    'guid': 'bar',
    'name': 'openscale-fake-instance',
    'region_id': 'us-south',
    'created_at': '2018-04-19T00:18:53.302077457Z',
    'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
    'resource_group_id': '0be5ad401ae913d8ff665d92680664ed',
    'crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
    'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c'
}
fake_key = {
    'id': 'crn:v1:staging:public:cloud-object-storage:global:a/4329073d16d2f3663f74bfa955259139:8d7af921-b136-4078-9666-081bd8470d94:resource-key:23693f48-aaa2-4079-b0c7-334846eff8d0',
    'guid': '23693f48-aaa2-4079-b0c7-334846eff8d0',
    'name': 'openscale-fastpath-credentials',
    'parameters': {
        'role_crn': 'crn:v1:bluemix:public:iam::::serviceRole:Writer'
    },
    'crn': 'crn:v1:staging:public:cloud-object-storage:global:a/4329073d16d2f3663f74bfa955259139:8d7af921-b136-4078-9666-081bd8470d94:resource-key:23693f48-aaa2-4079-b0c7-334846eff8d0',
    'resource_group_id': '0be5ad401ae913d8ff665d92680664ed',
    'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c',
    'credentials': {
        'apikey': 'XXXX-YYYY-ZZZZ',
        'url': 'https://cloud.ibm.com',
    }
}


@responses.activate
def test_create_instance_key():
    rc = ResourceController(access_token=fake_access_token)
    url = '{0}/v2/resource_keys'.format(base_url)
    request_data = {
        'source': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
        'role': 'Writer'
    }
    responses.add(
        responses.POST,
        url,
        body=json.dumps(fake_key),
        status=201,
        content_type='application/json')

    response = rc.create_instance_key(
        source=request_data['source'],
        role=request_data['role'])

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert response == fake_key


@responses.activate
def test_list_instance_keys():
    rc = ResourceController(access_token=fake_access_token)
    url = '{0}/v2/resource_instances/{1}/resource_keys'.format(
        base_url, 'guid-foo')
    expected = {
        'resources': [fake_key],
        'rows_count': 1
    }
    responses.add(
        responses.GET,
        url,
        body=json.dumps(expected),
        status=200,
        content_type='application/json')

    response = rc.list_instance_keys(guid='guid-foo')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert response == expected


@responses.activate
def test_delete_instance_key():
    rc = ResourceController(access_token=fake_access_token)
    guid = '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8'
    url = '{0}/v2/resource_keys/{1}'.format(base_url, guid)
    responses.add(
        responses.DELETE,
        url,
        body='',
        status=200)

    rc.delete_instance_key(guid=guid)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)


@responses.activate
def test_get_or_create_instance():
    rc = ResourceController(access_token=fake_access_token)
    expected_instances = {
        'resources': [fake_instance],
        'rows_count': 1
    }
    responses.add(
        responses.GET,
        '{0}/v2/resource_instances?resource_id=foo'.format(base_url),
        body=json.dumps(expected_instances),
        status=200,
        content_type='application/json')

    expected_keys = {
        'resources': [fake_key],
        'rows_count': 1
    }
    responses.add(
        responses.GET,
        '{0}/v2/resource_instances/{1}/resource_keys'.format(
            base_url, fake_instance['guid']),
        body=json.dumps(expected_keys),
        status=200,
        content_type='application/json')

    response = rc.get_or_create_instance(
        resource_id='foo',
        resource_name='openscale-fake-instance',
        resource_plan_id='resource_plan_id',
        resource_group='resource_group',
        target='us-south')

    assert len(responses.calls) == 2
    assert response['id'] == fake_instance['guid']
    assert response['crn'] == fake_instance['crn']
    assert response['created_at'] == fake_instance['created_at']
    assert response['credentials'] == fake_key['credentials']


@responses.activate
def test_create_instance():
    rc = ResourceController(access_token=fake_access_token)
    url = '{0}/v2/resource_instances'.format(base_url)
    expected = {
        'id': 'instance_ids',
        'name': 'openscale-fake-instance',
        'region_id': 'us-south',
        'created_at': '2018-04-19T00:18:53.302077457Z',
        'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
        'resource_group_id': '0be5ad401ae913d8ff665d92680664ed',
        'crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
        'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c'
    }
    responses.add(
        responses.POST,
        url,
        body=json.dumps(expected),
        status=201,
        content_type='application/json')

    response = rc.create_instance(
        name=expected['name'],
        target=expected['region_id'],
        resource_group=expected['resource_group_id'],
        resource_plan_id=expected['resource_plan_id'])

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert response == expected


@responses.activate
def test_list_instances():
    rc = ResourceController(access_token=fake_access_token)
    url = '{0}/v2/resource_instances?resource_id=foo'.format(base_url)
    expected = {
        'resources': [{
            'id': 'instance_ids',
            'guid': 'instance_ids',
            'name': 'openscale-fake-instance',
            'region_id': 'us-south',
            'created_at': '2018-04-19T00:18:53.302077457Z',
            'resource_plan_id': '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8',
            'resource_group_id': '0be5ad401ae913d8ff665d92680664ed',
            'crn': 'crn:v1:public:public:service_name:global:a/foo:instance_ids::',
            'resource_id': 'dff97f5c-bc5e-4455-b470-411c3edbe49c'
        }]
    }
    responses.add(
        responses.GET,
        url,
        body=json.dumps(expected),
        status=200,
        content_type='application/json')

    response = rc.list_instances(resource_id='foo')

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
    assert response == expected


@responses.activate
def test_delete_instance():
    rc = ResourceController(access_token=fake_access_token)
    resource_id = '2fdf0c08-2d32-4f46-84b5-32e0c92fffd8'
    url = '{0}/v2/resource_instances/{1}'.format(base_url, resource_id)
    responses.add(
        responses.DELETE,
        url,
        body='',
        status=200)

    rc.delete_instance(guid=resource_id)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.startswith(url)
