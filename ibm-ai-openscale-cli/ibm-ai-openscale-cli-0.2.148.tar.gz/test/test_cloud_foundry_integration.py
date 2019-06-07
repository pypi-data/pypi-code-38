# coding=utf-8

import os
import pytest
from unittest import TestCase
from ibm_ai_openscale_cli.setup_classes.token_manager import TokenManager
from ibm_ai_openscale_cli.setup_classes.cloud_foundry import CloudFoundry

base_url = 'https://api.ng.bluemix.net'

ASSISTANT_LITE_PLAN = '805f3109-79db-4b3b-ad5a-f17273ffc4fd'

@pytest.mark.skip(reason="CF is not used (Mar 28 2019)")
@pytest.mark.skipif(os.getenv('APIKEY') is None, reason='requires APIKEY')
class CloudFoundryTests(TestCase):
    def setUp(self):
        token_manager = TokenManager(
            apikey=os.environ['APIKEY'], iam_token=False)
        access_token = token_manager.get_token()
        self.cloud_foundry = CloudFoundry(
            access_token=access_token)

    def test_get_user(self):
        user = self.cloud_foundry.get_user()
        assert user

    def test_list_spaces(self):
        user = self.cloud_foundry.get_user()
        spaces = self.cloud_foundry.list_spaces(user['user_id'])
        assert spaces

    def test_list_instances(self):
        service_name = 'conversation'
        instances = self.cloud_foundry.list_instances(service_name)
        assert instances

    def test_list_instance_keys(self):
        service_name = 'conversation'
        instances = self.cloud_foundry.list_instances(service_name)
        assert instances

        guid = instances[0]['metadata']['guid']
        keys = self.cloud_foundry.list_instance_keys(guid=guid)
        assert keys

    def test_list_plans(self):
        service = self.cloud_foundry.get_service_by_name('conversation')
        plans = self.cloud_foundry.list_plans_by_service(
            service['metadata']['guid'])
        assert plans

    def test_get_or_create_instance(self):
        instance = self.cloud_foundry.get_or_create_instance(
            service_name='conversation',
            service_plan_guid=ASSISTANT_LITE_PLAN,
            organization_name='WatsonPlatformServices',
            space_name='demos')
        assert instance
        assert instance['credentials']

    def test_create_instance(self):
        user = self.cloud_foundry.get_user()
        spaces = self.cloud_foundry.list_spaces(user['user_id'])
        instance = self.cloud_foundry.create_instance(
            name='openscale-batman',
            service_plan_guid=ASSISTANT_LITE_PLAN,
            space_guid=spaces[0]['metadata']['guid'])
        assert instance
        self.cloud_foundry.delete_instance(instance['metadata']['guid'])
