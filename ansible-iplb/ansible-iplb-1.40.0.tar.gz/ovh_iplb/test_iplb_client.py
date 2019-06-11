from mock import patch
import unittest
from ovh_iplb import iplb_client
import ovh


class TestRealPayloadOkWithWantedPayload(unittest.TestCase):
    def test_with_unicode_on_real_payload(self):
        self.assertTrue(iplb_client._real_payload_ok_with_wanted_payload({u'key': u'val'}, {'key': 'val'}))
        self.assertFalse(iplb_client._real_payload_ok_with_wanted_payload({u'key': u'val2', 'key1': 'val1'},
                                                                          {'key': 'val', 'key1': 'val1'}))

    def test_when_real_payload_have_extra_field(self):
        self.assertTrue(iplb_client._real_payload_ok_with_wanted_payload(
            {'key': 'val', 'not_tracked_field': 'not_tracked'},
            {'key': 'val'}))

        self.assertFalse(iplb_client._real_payload_ok_with_wanted_payload(
            {'key': 'val', 'not_tracked_field': 'not_tracked'},
            {'key': 'val2'}))

    def test_when_wanted_payload_has_none(self):
        self.assertTrue(iplb_client._real_payload_ok_with_wanted_payload(
            {'key': 'val'},
            {'key': None}))

        self.assertFalse(iplb_client._real_payload_ok_with_wanted_payload(
            {'key': 'val', 'other': 'val'},
            {'key': None, 'other': 'valv2'}))

    def test_when_real_payload_is_missing_field(self):
        self.assertFalse(iplb_client._real_payload_ok_with_wanted_payload({}, {'key': 'val'}))

        self.assertFalse(iplb_client._real_payload_ok_with_wanted_payload(
            {'other': 'val'},
            {'key': 'val', 'other': 'val'}))


class PrepareMockedIPLB(object):
    def setUp(self):
        self.patcher = patch('ovh_iplb.iplb_client.ovh.Client')
        ovh = self.patcher.start()
        self.iplb_id = 'iplb_id'

        iplb_secret = {
            'endpoint': 'endpoint',
            'application_key': 'application_key',
            'application_secret': 'application_secret',
            'consumer_key': 'consumer_key'
        }

        self.iplb = iplb_client.IPLB(dict(iplb_id='iplb_id', timeout=2, **iplb_secret))
        ovh.assert_called_with(**iplb_secret)
        self.mocked_client_instance = self.iplb._client

    def mock_get(self, dic):
        def side_effect(path):
            if path in dic:
                value = dic[path]
                if value is not None:
                    return value
                else:
                    raise ovh.ResourceNotFoundError('')
            else:
                raise ValueError('Unexpected path call for get: "%s"' % (path,))

        self.mocked_client_instance.get.side_effect = side_effect

    def tearDown(self):
        self.patcher.stop()


class TestIplb(PrepareMockedIPLB, unittest.TestCase):
    def setUp(self):
        PrepareMockedIPLB.setUp(self)

    def tearDown(self):
        PrepareMockedIPLB.tearDown(self)

    def test_task_in_progress_when_no_task(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/task': [],
        })

        self.assertFalse(self.iplb.task_in_progress())

    def test_task_in_progress_when_task_not_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/task': [1, 2],
            '/ipLoadbalancing/iplb_id/task/1': {'status': 'doing'},
            '/ipLoadbalancing/iplb_id/task/2': {'status': 'done'},
        })

        self.assertTrue(self.iplb.task_in_progress())

    def test_task_in_progress_when_all_task_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/task': [1, 2],
            '/ipLoadbalancing/iplb_id/task/1': {'status': 'done'},
            '/ipLoadbalancing/iplb_id/task/2': {'status': 'done'},
        })

        self.assertFalse(self.iplb.task_in_progress())

    def test_is_refresh_needed_when_no_pending_change(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/pendingChanges': [],
        })
        self.assertFalse(self.iplb.is_refresh_needed())

        self.mock_get({
            '/ipLoadbalancing/iplb_id/pendingChanges': [{'number': 0, 'zone': 'gra'}, {'number': 0, 'zone': 'rbx'}],
        })

        self.assertFalse(self.iplb.is_refresh_needed())

    def test_is_refresh_needed_when_pending_change(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/pendingChanges': [],
        })
        self.assertFalse(self.iplb.is_refresh_needed())

        self.mock_get({
            '/ipLoadbalancing/iplb_id/pendingChanges': [{'number': 0, 'zone': 'gra'}, {'number': 1, 'zone': 'rbx'}],
        })

        self.assertTrue(self.iplb.is_refresh_needed())

    def test_refresh(self):
        self.iplb.refresh()
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/refresh')


class TestFrontend(PrepareMockedIPLB, unittest.TestCase):
    def setUp(self):
        PrepareMockedIPLB.setUp(self)

    def tearDown(self):
        PrepareMockedIPLB.tearDown(self)

    def test_exist_with_unexisting_id(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/frontend/42': None,
        })
        self.assertFalse(self.iplb.frontend({
            'type': 'tcp',
            'id': 42
        }).exist())

    def test_exist_with_existing_id(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/frontend/42': {'displayName': 'name'}
        })
        self.assertTrue(self.iplb.frontend({
            'type': 'tcp',
            'id': 42,
            'default_farm_name': 'farm_name'
        }).exist())

    def test_exist_with_unexisting_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/frontend/42': {'frontendId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/frontend': ['42']
        })
        self.assertFalse(self.iplb.frontend({
            'type': 'tcp',
            'name': 'bad_name'
        }).exist())

    def test_exist_with_existing_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        self.assertTrue(self.iplb.farm({
            'type': 'tcp',
            'name': 'name'
        }).exist())

    def test_exist_with_duplicated_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/frontend/42': {'frontenId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/frontend/41': {'frontenId': 41, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/frontend': ['41', '42']
        })
        with self.assertRaises(ValueError):
            self.iplb.frontend({
                'type': 'tcp',
                'name': 'name',
                'default_farm_name': 'name'

            }).exist()

    def test_create_should_fail_when_no_farm_with_given_name_exist(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42'],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'}
        })
        with self.assertRaises(ValueError):
            self.iplb.frontend({
                'id': '123456789',
                'type': 'tcp',
                'allowed_source': '1.2.3.4',
                'dedicated_ipfo': '6.6.6.6',
                'default_farm_name': 'bad_name',
                'default_ssl_id': 666,
                'disabled': False,
                'name': 'name',
                'http_header': 'X-super-header',
                'hsts': False,
                'port': '666',
                'redirect_location': 'to_bikkini_bottom',
                'ssl': False,
                'zone': 'all'
             }).body()

    def test_body_with_default_farm_id(self):
        self.assertEqual(self.iplb.frontend({
            'id': '123456789',
            'type': 'tcp',
            'allowed_source': '1.2.3.4',
            'dedicated_ipfo': '6.6.6.6',
            'default_farm_id': 1234,
            'default_ssl_id': 666,
            'disabled': False,
            'name': 'name',
            'http_header': 'X-super-header',
            'hsts': False,
            'port': '666',
            'redirect_location': 'to_bikkini_bottom',
            'ssl': False,
            'zone': 'all'
        }).body(), {
            'displayName': 'name',
            'port': '666',
            'zone': 'all',
            'allowedSource': '1.2.3.4',
            'dedicatedIpfo': '6.6.6.6',
            'defaultFarmId': 1234,
            'defaultSslId': 666,
            'disabled': False,
            'hsts': False,
            'httpHeader': 'X-super-header',
            'redirectLocation': 'to_bikkini_bottom',
            'ssl': False
        })

    def test_body_when_default_farm_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42'],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'}
        })
        with self.assertRaises(ValueError):
            self.assertEqual(
                self.iplb.frontend({
                    'id': '123456789',
                    'type': 'tcp',
                    'allowed_source': '1.2.3.4',
                    'dedicated_ipfo': '6.6.6.6',
                    'default_farm_name': 'name',
                    'default_name_id': None,
                    'default_ssl_id': 666,
                    'disabled': False,
                    'name': 'name',
                    'http_header': 'X-super-header',
                    'hsts': False,
                    'port': '666',
                    'redirect_location': 'to_bikkini_bottom',
                    'ssl': False,
                    'zone': 'all'
                }).body(),
                {
                    'displayName': 'name',
                    'port': '666',
                    'zone': 'all',
                    'allowedSource': '1.2.3.4',
                    'dedicatedIpfo': '6.6.6.6',
                    'defaultFarmId': 42,
                    'defaultSslId': 666,
                    'disabled': False,
                    'hsts': False,
                    'httpHeader': 'X-super-header',
                    'redirectLocation': 'to_bikkini_bottom',
                    'ssl': False
                }
            )

    def test_body_with_both_default_farm_name_id(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42'],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'}
        })
        with self.assertRaises(ValueError):
            self.iplb.frontend({
                'id': '123456789',
                'type': 'tcp',
                'allowed_source': '1.2.3.4',
                'dedicated_ipfo': '6.6.6.6',
                'default_farm_id': '42',
                'default_farm_name': 'name',
                'default_ssl_id': 666,
                'disabled': False,
                'name': 'name',
                'http_header': 'X-super-header',
                'hsts': False,
                'port': '666',
                'redirect_location': 'to_bikkini_bottom',
                'ssl': False,
                'zone': 'all'
                }).body()

    def test_read(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/frontend/42': {'frontendId': 42, 'displayName': 'name', 'field': 'data'},
            '/ipLoadbalancing/iplb_id/tcp/frontend/41': {'frontendId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/frontend': ['41', '42']
        })

        self.assertEqual(self.iplb.frontend({'type': 'tcp', 'name': 'name'}).read(), {'frontendId': 42,
                                                                                      'displayName': 'name',
                                                                                      'field': 'data'})

    def test_create(self):
        self.iplb.frontend({'default_farm_id': 42, 'type': 'tcp', 'name': 'name', 'zone': 'gra'}).create()
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/frontend',
                                                            displayName='name',
                                                            defaultFarmId=42,
                                                            zone='gra')


class TestFarm(PrepareMockedIPLB, unittest.TestCase):
    def setUp(self):
        PrepareMockedIPLB.setUp(self)

    def tearDown(self):
        PrepareMockedIPLB.tearDown(self)

    def test_exist_with_unexisting_id(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': None,
        })
        self.assertFalse(self.iplb.farm({
            'type': 'tcp',
            'id': 42
        }).exist())

    def test_exist_with_existing_id(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'displayName': 'name'},
        })
        self.assertTrue(self.iplb.farm({
            'type': 'tcp',
            'id': 42
        }).exist())

    def test_exist_with_unexisting_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        self.assertFalse(self.iplb.farm({
            'type': 'tcp',
            'name': 'bad_name'
        }).exist())

    def test_exist_with_existing_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        self.assertTrue(self.iplb.farm({
            'type': 'tcp',
            'name': 'name'
        }).exist())

    def test_exist_with_duplicated_name(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'name'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42']
        })
        with self.assertRaises(ValueError):
            self.iplb.farm({
                'type': 'tcp',
                'name': 'name'
            }).exist()

    def test_body(self):
        self.assertEqual(self.iplb.farm({
            'name': 'name',
            'port': 4343,
            'probe': {'probe1': 'probe2'},
            'type': 'tcp',
            'balance': 'balance',
            'zone': 'zone',
            'stickiness': 'stickiness',
            'vrack_network_id': 'vrackNetworkId',
            'server': 'val'
        }).body(), {
            'displayName': 'name',
            'port': 4343,
            'probe': {'probe1': 'probe2'},
            'balance': 'balance',
            'zone': 'zone',
            'stickiness': 'stickiness',
            'vrackNetworkId': 'vrackNetworkId',
        })

    def test_read(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'field': 'data'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42']
        })

        self.assertEqual(self.iplb.farm({'type': 'tcp', 'name': 'name'}).read(), {'farmId': 42,
                                                                                  'displayName': 'name',
                                                                                  'field': 'data'})

    def test_create(self):
        self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'gra'}).create()
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm',
                                                            displayName='name',
                                                            zone='gra')

    def test_update_when_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'field': 'data'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42']
        })

        self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'gra'}).update()
        self.mocked_client_instance.put.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42',
                                                           displayName='name',
                                                           zone='gra')

    def test_update_when_no_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42']
        })

        self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'gra'}).update()
        self.mocked_client_instance.put.assert_not_called()

    def test_apply_when_creation_needed2(self):
        self.mocked_client_instance.post.return_value = {'farmId': 42}
        self.mock_get({'/ipLoadbalancing/iplb_id/tcp/farm/42/server': [],
                       '/ipLoadbalancing/iplb_id/tcp/farm': []})
        self.assertTrue(self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'gra'}).apply())
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm',
                                                            displayName='name',
                                                            zone='gra')

    def test_apply_when_update_needed(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        self.assertTrue(self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'all'}).apply())
        self.mocked_client_instance.put.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42',
                                                           displayName='name',
                                                           zone='all')

    def test_apply_when_no_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42']
        })

        self.assertFalse(self.iplb.farm({'type': 'tcp', 'name': 'name', 'zone': 'gra'}).apply())
        self.mocked_client_instance.put.assert_not_called()

    def test_apply_with_new_servers(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [],
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42'],
        })

        self.assertTrue(self.iplb.farm({'type': 'tcp',
                                        'name':
                                        'name',
                                        'zone': 'gra',
                                        'servers': [{'address': '8.8.8.8'}]}).apply())

        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server',
                                                            address='8.8.8.8')

    def test_apply_with_servers_to_update(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42'],
        })

        self.assertTrue(self.iplb.farm({'type': 'tcp',
                                        'name':
                                        'name',
                                        'zone': 'gra',
                                        'servers': [{'address': '8.8.8.8', 'display_name': 'server1'}]}).apply())

        self.mocked_client_instance.put.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server/1',
                                                           displayName='server1',
                                                           address='8.8.8.8')

    def test_apply_with_servers_to_delete(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.8.9', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm/41': {'farmId': 41, 'displayName': 'otherName'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['41', '42'],
        })

        self.assertTrue(self.iplb.farm({'type': 'tcp',
                                        'name':
                                        'name',
                                        'zone': 'gra',
                                        'servers': [{'address': '8.8.8.8'}]}).apply())

        self.mocked_client_instance.delete.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server/2')


class TestServer(PrepareMockedIPLB, unittest.TestCase):
    def setUp(self):
        PrepareMockedIPLB.setUp(self)

    def tearDown(self):
        PrepareMockedIPLB.tearDown(self)

    def test_exist_with_unexisting_address(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '1.3.4.5', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '1.3.4.6', 'serverId': 2},
        })
        self.assertFalse(self.iplb.farm({
            'type': 'tcp',
            'id': 42
        }).server({'address': '8.8.8.8'}).exist())

    def test_exist_with_existing_address(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '1.3.4.6', 'serverId': 2},
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'displayName': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        self.assertTrue(self.iplb.farm({
            'type': 'tcp',
            'name': 'name'
        }).server({'address': '8.8.8.8'}).exist())

    def test_exist_with_duplicated_address(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8', 'serverId': 1},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.8.8', 'serverId': 2},
            '/ipLoadbalancing/iplb_id/tcp/farm/42': {'farmId': 42, 'display_name': 'name', 'zone': 'gra'},
            '/ipLoadbalancing/iplb_id/tcp/farm': ['42']
        })
        with self.assertRaises(ValueError):
            self.iplb.farm({
                'type': 'tcp',
                'id': 'name'
            }).server({'address': '8.8.8.8'}).exist()

    def test_body(self):
        self.assertEqual(self.iplb.farm({
            'name': 'name',
        }).server({
            'address': '8.8.1.4',
            'server_id': 'serverId',
            'backup': True,
            'chain': 'chain',
            'display_name': 'one has no name',
            'port': 8080,
            'probe': False,
            'proxy_protocol_version': 'v1',
            'ssl': True,
            'status': 'active',
            'weight': 2
        }).body(), {
            'address': '8.8.1.4',
            'backup': True,
            'chain': 'chain',
            'displayName': 'one has no name',
            'port': 8080,
            'probe': False,
            'proxyProtocolVersion': 'v1',
            'ssl': True,
            'status': 'active',
            'weight': 2
        })

        self.assertEqual(self.iplb.farm({
            'name': 'name',
        }).server({
            'address': '8.8.1.4'
        }).body(), {
            'address': '8.8.1.4'
        })

    def test_read(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7', 'serverId': 2},
        })

        self.assertEqual(
            self.iplb.farm({'type': 'tcp', 'id': 42}).server({'address': '8.8.8.8'}).read(),
            {'serverId': 1, 'displayName': 'server1', 'address': '8.8.8.8'})

    def test_create(self):
        self.iplb.farm({'type': 'tcp', 'id': '42'}).server({'address': '8.8.5.6', 'display_name': 'server1'}).create()
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server',
                                                            displayName='server1',
                                                            address='8.8.5.6')

    def test_update_when_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7', 'serverId': 2},
        })

        changement = self.iplb.farm({'type': 'tcp', 'id': '42'})\
                              .server({'address': '8.8.8.8', 'display_name': 'newName'})\
                              .update()

        self.mocked_client_instance.put.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server/1',
                                                           address='8.8.8.8',
                                                           displayName='newName')
        self.assertTrue(changement)

    def test_update_when_no_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7', 'serverId': 2},
        })

        changement = self.iplb.farm({'type': 'tcp', 'id': '42'})\
                              .server({'address': '8.8.8.8', 'display_name': 'server1'})\
                              .update()

        self.mocked_client_instance.put.assert_not_called()
        self.assertFalse(changement)

    def test_apply_when_creation_needed(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7',
                                                              'serverId': 2},
        })
        changement = self.iplb.farm({'type': 'tcp', 'id': '42'})\
                              .server({'address': '8.8.8.9', 'display_name': 'server3'})\
                              .apply()
        self.mocked_client_instance.post.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server',
                                                            displayName='server3',
                                                            address='8.8.8.9')
        self.assertTrue(changement)

    def test_apply_when_update_needed(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7',
                                                              'serverId': 2},
        })

        changement = self.iplb.farm({'type': 'tcp', 'id': '42'})\
                              .server({'address': '8.8.8.8', 'display_name': 'newName'})\
                              .apply()

        self.mocked_client_instance.put.assert_called_with('/ipLoadbalancing/iplb_id/tcp/farm/42/server/1',
                                                           address='8.8.8.8',
                                                           displayName='newName')
        self.assertTrue(changement)

    def test_apply_when_no_change_to_be_done(self):
        self.mock_get({
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server': [1, 2],
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/1': {'address': '8.8.8.8',
                                                              'serverId': 1,
                                                              'displayName': 'server1'},
            '/ipLoadbalancing/iplb_id/tcp/farm/42/server/2': {'address': '8.8.7.7',
                                                              'serverId': 2},
        })

        changement = self.iplb.farm({'type': 'tcp', 'id': '42'})\
                              .server({'address': '8.8.8.8', 'display_name': 'server1'})\
                              .apply()

        self.mocked_client_instance.put.assert_not_called()
        self.assertFalse(changement)


if __name__ == '__main__':
    unittest.main()
