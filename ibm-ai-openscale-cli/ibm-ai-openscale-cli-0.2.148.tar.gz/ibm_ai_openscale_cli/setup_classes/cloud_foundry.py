# coding=utf-8
from __future__ import print_function
import json as json_import
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import requests
import time
from retry import retry
from ibm_ai_openscale_cli.utility_classes.utils import get_error_message

logger = FastpathLogger(__name__)

DEFAULT_URL = 'https://api.ng.bluemix.net'
USER_INFO_URL = 'https://uaa.ng.bluemix.net/userinfo'

POSTGRES_SERVICE_NAME = 'compose-for-postgresql'
POSTGRES_STANDARD_PLAN_GUID = '21519603-6bfd-4e58-939a-b75ef167dbf2'  # Standard
SPARK_SERVICE_NAME = 'spark'
# ibm.SparkService.PayGoPersonal
SPARK_PLAN_GUID = 'e82167fb-4c35-4c65-ba3d-cfe355e6cb45'


def find_by_name(resources, name):
    for res in resources:
        if res['entity']['name'] == name:
            return res
    return None

class CloudFoundry(object):

    def __init__(self, access_token, url=DEFAULT_URL):
        """CloudFoundry

        Arguments:
            access_token {string} -- IAA/UAA access token

        Keyword Arguments:
            url {string} -- CloudFoundry URL. Different for each region (default: https://api.ng.bluemix.net)
        """

        self.url = url
        self.access_token = access_token


    def _request(self, method, url, headers=None, params=None, data=None, json_data=None, accept_json=True, **kwargs):
        full_url = self.url + url if url.startswith('/') else url

        headers = headers if headers else {}
        headers.update({
            'Authorization': 'Bearer {0}'.format(self.access_token)
        })
        if accept_json:
            headers['accept'] = 'application/json'

        if not data and json_data is not None:
            data = json_import.dumps(json_data)
            headers.update({'content-type': 'application/json'})

        response = requests.request(method=method, url=full_url,
                                    headers=headers, params=params,
                                    data=data, **kwargs)

        if 200 <= response.status_code <= 299:
            return response.json() if accept_json else response.text

        raise Exception(get_error_message(response))

    def get_user(self):
        """Returns the user information based on the existing access_token

        Returns:
            dict -- The user information
        """

        logger.log_debug('CloudFoundry.get_user()')
        response = self._request(
            method='GET',
            url=USER_INFO_URL
        )
        return response

    def list_spaces(self, user_id):
        """List the CF spaces where the user is a developer

        Arguments:
            user_id {string} -- The user id

        Returns:
            list -- List of spaces. See: https://apidocs.cloudfoundry.org/1.23.0/users/list_all_spaces_for_the_user.html
        """

        logger.log_debug('CloudFoundry.list_spaces()')
        response = self._request(
            method='GET',
            url='/v2/users/{0}/spaces'.format(user_id)
        )

        return response['resources']

    def list_organizations(self, user_id):
        """List the CF organizations where the user is a developer

        Arguments:
            user_id {string} -- The user id

        Returns:
            list -- List of organizations.
        """

        logger.log_debug('CloudFoundry.list_organizations()')
        response = self._request(
            method='GET',
            url='/v2/users/{0}/organizations'.format(user_id)
        )

        return response['resources']

    def get_service_by_name(self, name):
        logger.log_debug('CloudFoundry.get_service_by_name()')
        response = self._request(
            method='GET',
            url='/v2/services',
            params={'q': 'label:{0}'.format(name)})

        if response['total_results'] == 0:
            raise Exception('{0} service cannot be found'.format(name))

        return response['resources'][0]

    def list_plans_by_service(self, service_guid):
        logger.log_debug('CloudFoundry.list_plans_by_service()')
        response = self._request(
            method='GET',
            url='/v2/services/{0}/service_plans'.format(service_guid))

        return response['resources']

    def list_instances_by_plan(self, plan, spaces=None):
        logger.log_debug('CloudFoundry.list_instances_by_plan()')
        if not spaces:
            user = self.get_user()
            spaces = self.list_spaces(user['user_id'])

        space_guids = [s['metadata']['guid'] for s in spaces]
        spaces_filter = 'space_guid IN {0}'.format(','.join(space_guids))
        params = {'q': spaces_filter}

        response = self._request(
            method='GET',
            url='/v2/service_plans/{0}/service_instances'.format(plan),
            params=params)

        return response['resources']

    def list_instances(self, service_name, spaces=None):
        logger.log_debug('CloudFoundry.list_instances()')
        service = self.get_service_by_name(service_name)
        plans = self.list_plans_by_service(service['metadata']['guid'])

        instances = []
        for plan in plans:
            instances += self.list_instances_by_plan(plan['metadata']['guid'], spaces)

        return instances

    def create_instance(self, name, service_plan_guid, space_guid):
        logger.log_debug('CloudFoundry.create_instance()')
        data = {
            'name': name,
            'service_plan_guid': service_plan_guid,
            'space_guid': space_guid,
            'tags': ['self-created']
        }
        response = self._request(
            method='POST',
            url='/v2/service_instances',
            json_data=data,
            params={'accepts_incomplete': 'false'})

        return response

    def delete_instance(self, guid):
        logger.log_debug('CloudFoundry.delete_instance()')
        response = self._request(
            method='DELETE',
            accept_json=False,
            params={'recursive': 'true', 'accepts_incomplete': 'false'},
            url='/v2/service_instances/{0}'.format(guid))

        return response

    def create_instance_key(self, service_instance_guid):
        logger.log_debug('CloudFoundry.create_instance_key()')
        data = {
            'service_instance_guid': service_instance_guid,
            'name': 'fastpath-credentials'
        }
        response = self._request(
            method='POST',
            url='/v2/service_keys',
            json_data=data)

        return response

    def list_instance_keys(self, guid):
        logger.log_debug('CloudFoundry.list_instance_keys()')
        response = self._request(
            method='GET',
            url='/v2/service_instances/{0}/service_keys'.format(guid))

        return response['resources']

    def delete_instance_key(self, guid):
        logger.log_debug('CloudFoundry.delete_instance_key()')
        response = self._request(
            method='DELETE',
            url='/v2/resource_keys/{0}'.format(guid),
            accept_json=False)

        return response

    @retry(tries=5, delay=1, backoff=2)
    def get_or_create_instance(self, service_name, service_instance_name=None, service_plan_guid=None, organization_name=None, space_name=None):
        """Returns a service instance.
        If there is no instance available, a new one is provisioned.
        If there is no existing service key, a new one is created.

        Arguments:
            service_name {string} -- service label, e.g.: conversation, spark, compose-for-postgres
            service_plan_guid {string} -- service plan guid label, e.g.: 21519603-6bfd-4e58-939a-b75ef167dbf2
            organization_name {string} -- Organization label
            space_name {string} -- space label

        Returns:
            dict -- The service instance with valid credentials, dictionary with: id, name, created_at and credentials
        """
        logger.log_debug('CloudFoundry.get_or_create_instance(): service name: %s, plan: %s', service_name, service_plan_guid)

        user = self.get_user()
        organizations = self.list_organizations(user['user_id'])
        spaces = self.list_spaces(user['user_id'])
        space = spaces[0]

        if organization_name and space_name:
            organization = find_by_name(organizations, organization_name)
            if not organization:
                raise Exception(organization_name + ' not found')
            spaces = [spa for spa in spaces if spa['entity']['organization_guid'] == organization['metadata']['guid']]
            space = find_by_name(spaces, space_name)
            if not space:
                raise Exception(space_name + ' not found')

        # Find instances independendly of the plan.
        # If organization_name and space_name were specified only look for instances
        # in the organization.
        instances = self.list_instances(service_name=service_name, spaces=spaces)
        instance = instances[0] if instances else None

        if not instance:
            name = service_instance_name if service_instance_name else 'openscale-{0}-{1}'.format(service_name, time.time())
            instance = self.create_instance(
                name=name,
                service_plan_guid=service_plan_guid,
                space_guid=space['metadata']['guid']
            )

        keys = self.list_instance_keys(instance['metadata']['guid'])
        key = keys[0] if keys else None

        if not key:
            key = self.create_instance_key(
                service_instance_guid=instance['metadata']['guid']
            )

        instance['entity']['credentials'] = key['entity']['credentials']
        return {
            'id': instance['metadata']['guid'],
            'name': instance['entity']['name'],
            'created_at': instance['metadata']['created_at'],
            'credentials': key['entity']['credentials']
        }

    def __str__(self):
        return 'CloudFoundry: url: {1}, access_token: {0}'.format(self.url, self.access_token[:5])
