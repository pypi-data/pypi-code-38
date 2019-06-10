
from unittest import TestCase
from lando.server.cloudservice import CloudService
from unittest import mock


class TestCloudService(TestCase):
    @mock.patch('lando.server.cloudservice.CloudClient')
    def test_makes_cloud_client(self, mock_cloud_client):
        mock_credentials = mock.Mock()  # a function that returns credentials
        config = mock.MagicMock(cloud_settings=mock.MagicMock(credentials=mock_credentials))
        vm_settings = mock.MagicMock(vm_project_name='test-project')
        service = CloudService(config, vm_settings)
        self.assertEqual(service.vm_settings, vm_settings)

        # Assert that mock_credentials was called with the vm_project_name
        args, kwargs = mock_credentials.call_args
        self.assertEqual(args[0], 'test-project')

        # Assert that CloudClient is called with the return value of credentials
        args, kwargs = mock_cloud_client.call_args
        self.assertEqual(args[0], mock_credentials.return_value)

    @mock.patch('lando.server.cloudservice.shade')
    def test_that_flavor_overrides_default(self, mock_shade):
        config = mock.MagicMock()
        vm_settings = mock.MagicMock()
        cloud_service = CloudService(config, vm_settings)
        cloud_service.launch_instance(server_name="worker1", flavor_name='m1.GIANT', script_contents="",
                                      volumes=['volume1'])
        mock_shade.openstack_cloud()
        mock_shade.openstack_cloud().create_server.assert_called()
        args, kw_args = mock_shade.openstack_cloud().create_server.call_args
        self.assertEqual(kw_args['flavor'], 'm1.GIANT')

    @mock.patch('lando.server.cloudservice.shade')
    def test_launch_instance_no_floating_ip(self, mock_shade):
        mock_shade.openstack_cloud().create_server.return_value = mock.Mock(accessIPv4='')
        config = mock.MagicMock(vm_settings=mock.Mock(image_name='myvm', floating_ip_pool_name='somepool'))
        vm_settings = mock.MagicMock(allocate_floating_ips=False)
        cloud_service = CloudService(config, vm_settings)
        instance, ip_address = cloud_service.launch_instance(server_name="worker1", flavor_name=None,
                                                             script_contents="", volumes=['volume1'])
        self.assertEqual('', ip_address)
        mock_shade.openstack_cloud().create_server.assert_called()
        args, kw_args = mock_shade.openstack_cloud().create_server.call_args
        self.assertEqual(kw_args['auto_ip'], False)
        self.assertEqual(kw_args['volumes'], ['volume1'])

    @mock.patch('lando.server.cloudservice.shade')
    def test_launch_instance_with_floating_ip(self, mock_shade):
        mock_shade.openstack_cloud().create_server.return_value = mock.Mock(accessIPv4='123')
        config = mock.MagicMock()
        vm_settings = mock.MagicMock(allocate_floating_ips=True)
        cloud_service = CloudService(config, vm_settings)
        instance, ip_address = cloud_service.launch_instance(server_name="worker1", flavor_name='flavor1',
                                                             script_contents="", volumes=['volume1'])
        self.assertNotEqual(None, ip_address)
        mock_shade.openstack_cloud().create_server.assert_called()
        args, kw_args = mock_shade.openstack_cloud().create_server.call_args
        self.assertEqual(kw_args['auto_ip'], True)

    @mock.patch('lando.server.cloudservice.shade')
    def test_terminate_instance_no_floating_ip(self, mock_shade):
        config = mock.MagicMock()
        vm_settings = mock.MagicMock(allocate_floating_ips=False)
        cloud_service = CloudService(config, vm_settings)
        cloud_service.terminate_instance(server_name='worker1', volume_names=[])
        mock_shade.openstack_cloud().delete_server.assert_called()
        args, kw_args = mock_shade.openstack_cloud().delete_server.call_args
        self.assertEqual(kw_args['delete_ips'], False)

    @mock.patch('lando.server.cloudservice.shade')
    def test_terminate_instance_with_floating_ip(self, mock_shade):
        config = mock.MagicMock()
        vm_settings = mock.MagicMock(allocate_floating_ips=True)
        cloud_service = CloudService(config, vm_settings)
        cloud_service.terminate_instance(server_name='worker1')
        args, kw_args = mock_shade.openstack_cloud().delete_server.call_args
        self.assertEqual(kw_args['delete_ips'], True)

    @mock.patch('lando.server.cloudservice.shade')
    def test_create_volume(self, mock_shade):
        mock_shade.openstack_cloud().create_volume.return_value = mock.Mock(id='volume-id1')
        config = mock.MagicMock()
        vm_settings = mock.MagicMock()
        cloud_service = CloudService(config, vm_settings)
        volume, volume_id = cloud_service.create_volume(100, 'volume1')
        self.assertIsNotNone(volume_id)
        mock_shade.openstack_cloud().create_volume.assert_called()
        args, kw_args = mock_shade.openstack_cloud().create_volume.call_args
        self.assertEqual(args, (100,))
        self.assertEqual(kw_args['name'], 'volume1')

    @mock.patch('lando.server.cloudservice.shade')
    def test_terminate_instance_with_volumes(self, mock_shade):
        config = mock.MagicMock()
        vm_settings = mock.MagicMock()
        cloud_service = CloudService(config, vm_settings)
        cloud_service.terminate_instance(server_name='worker1', volume_names=['volume1'])
        args, kw_args = mock_shade.openstack_cloud().delete_server.call_args
        self.assertEqual(args, ('worker1',))
        self.assertEqual(kw_args['wait'], True)
        args, kw_args = mock_shade.openstack_cloud().delete_volume.call_args
        self.assertEqual(args, ('volume1',))
        self.assertEqual(mock_shade.openstack_cloud().delete_volume.call_count, 1)

    @mock.patch('lando.server.cloudservice.shade')
    @mock.patch('lando.server.cloudservice.uuid')
    def test_make_volume_name(self, mock_uuid, mock_shade):
        mock_uuid.uuid4 = mock.Mock(return_value='uuid-1234')
        config = mock.MagicMock()
        vm_settings = mock.MagicMock()
        cloud_service = CloudService(config, vm_settings)
        volume_name = cloud_service.make_volume_name('6')
        self.assertEqual(volume_name, 'vol-job6_uuid-1234')
        self.assertTrue(mock_uuid.uuid4.called)

