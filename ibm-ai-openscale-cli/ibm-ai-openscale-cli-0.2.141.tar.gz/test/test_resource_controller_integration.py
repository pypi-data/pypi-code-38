# coding=utf-8

import os
import pytest
import time
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from ibm_ai_openscale_cli.setup_classes.resource_controller import ResourceController
from unittest import TestCase

ASSISTANT_RESOURCE_ID = '7045626d-55e3-4418-be11-683a26dbc1e5'
ASSISTANT_LITE_PLAN = 'bd16e3c8-3da0-11e6-bce3-54ee7514918e'
RESOURCE_GROUP = '47561d9f48cc499da14961c873109e5b'
RESOURCE_ID_MACHINE_LEARNING = '51c53b72-918f-4869-b834-2d99eb28422a'


@pytest.mark.skipif(
    os.getenv('APIKEY') is None, reason='requires APIKEY')
class ResourceControllerTests(TestCase):
    def setUp(self):
        token_manager = TokenManager(apikey=os.environ['APIKEY'])
        access_token = token_manager.get_token()
        self.resource_controller = ResourceController(
            access_token=access_token)

    def test_list_instances(self):
        instances = self.resource_controller.list_instances()
        assert len(instances['resources']) > 1

    def test_get_resource_group_by_name(self):
        resource_group = self.resource_controller.get_resource_group_by_name('developer-experience')
        assert resource_group

    def test_list_instances_keys(self):
        instances = self.resource_controller.list_instances()
        assert instances['resources']

        guid = instances['resources'][0]['guid']
        keys = self.resource_controller.list_instance_keys(guid=guid)

        assert keys

    def test_get_or_create_instance(self):
        instance = self.resource_controller.get_or_create_instance(
            resource_id=RESOURCE_ID_MACHINE_LEARNING)
        assert instance
        assert instance['credentials']

    def test_create_instance(self):
        instances = self.resource_controller.list_instances(
            resource_id=ASSISTANT_RESOURCE_ID)

        for i in instances['resources']:
            self.resource_controller.delete_instance(i['guid'], recursive=True)

        service_name = 'itest-{0}'.format(time.time())
        instance = self.resource_controller.create_instance(
            name=service_name,
            target='us-south',
            resource_group=RESOURCE_GROUP,
            resource_plan_id=ASSISTANT_LITE_PLAN)

        assert instance

        self.resource_controller.delete_instance(
            instance['guid'], recursive=True)
