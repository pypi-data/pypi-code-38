#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the uploader with httpretty."""
from unittest import TestCase
from json import dumps
import httpretty
from pacifica.policy.uploader.rest import UploaderPolicy
from pacifica.policy.config import get_config


class TestUploader(TestCase):
    """Test the uploader policy with httpretty."""

    sample_user_id = 23
    admin_user_id = 45
    admin_group_id = 127
    user_group_json = [
        {
            'group': admin_group_id,
            'person': admin_user_id
        }
    ]
    admin_group_json = [
        {
            '_id': admin_group_id
        }
    ]
    group_url = '{0}/groups'.format(
        get_config().get('metadata', 'endpoint_url')
    )
    user_group_url = '{0}/user_group'.format(
        get_config().get('metadata', 'endpoint_url')
    )

    @httpretty.activate
    def test_failed_admin_id(self):
        """check failed admin id fallback works."""
        httpretty.register_uri(httpretty.GET, self.group_url,
                               body=dumps([]),
                               content_type='application/json')
        httpretty.register_uri(httpretty.GET, self.user_group_url,
                               body=dumps([]),
                               content_type='application/json')
        upolicy = UploaderPolicy()
        # pylint: disable=no-member
        # pylint: disable=protected-access
        ret = upolicy._is_admin(10)
        # pylint: enable=protected-access
        # pylint: enable=no-member
        self.assertFalse(ret)
