from django import test
from ievv_opensource.ievv_sms import sms_registry
from unittest import mock


class TestRegistry(test.TestCase):
    def test_add_ok(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        registry.add(mock_backend_class)
        self.assertIn('mock', registry._backend_class_map)

    def test_add_failed(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        registry.add(mock_backend_class)
        with self.assertRaisesMessage(ValueError,
                                      "'mock' is already in the SMS backend registry."):
            registry.add(mock_backend_class)

    def test_remove(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        registry.add(mock_backend_class)
        self.assertIn('mock', registry._backend_class_map)
        registry.remove(mock_backend_class)
        self.assertNotIn('mock', registry._backend_class_map)

    def test_contains(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        registry.add(mock_backend_class)
        self.assertTrue(mock_backend_class in registry)

    def test_iter_backends(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class1 = mock.MagicMock()
        mock_backend_class1.get_backend_id.return_value = 'mock1'
        registry.add(mock_backend_class1)
        mock_backend_class2 = mock.MagicMock()
        mock_backend_class2.get_backend_id.return_value = 'mock2'
        registry.add(mock_backend_class2)
        self.assertEqual(set(registry.iter_backend_classes()), {
            mock_backend_class1, mock_backend_class2
        })

    def test__iter__(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class1 = mock.MagicMock()
        mock_backend_class1.get_backend_id.return_value = 'mock1'
        registry.add(mock_backend_class1)
        mock_backend_class2 = mock.MagicMock()
        mock_backend_class2.get_backend_id.return_value = 'mock2'
        registry.add(mock_backend_class2)
        self.assertEqual(set(iter(registry)), {
            mock_backend_class1, mock_backend_class2
        })

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID=None)
    def test_get_default_backend_id__default(self):
        registry = sms_registry.MockableRegistry()
        self.assertEqual(registry.get_default_backend_id(), 'debugprint')

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID='something')
    def test_get_default_backend_id__custom(self):
        registry = sms_registry.MockableRegistry()
        self.assertEqual(registry.get_default_backend_id(), 'something')

    def test_get_backend_class_by_id__ok(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        registry.add(mock_backend_class)
        self.assertEqual(registry.get_backend_class_by_id('mock'),
                         mock_backend_class)

    def test_get_backend_class_by_id__invalid_backend_id(self):
        registry = sms_registry.MockableRegistry()
        with self.assertRaises(KeyError):
            registry.get_backend_class_by_id('invalid')

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID='mock')
    def test_make_backend_instance__default_backend(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        mock_backend_instance = mock.MagicMock()
        mock_backend_class.return_value = mock_backend_instance
        registry.add(mock_backend_class)
        backend = registry.make_backend_instance(
            phone_number='12345678',
            message='Testmessage'
        )
        mock_backend_class.assert_called_once_with(
            phone_number='12345678',
            message='Testmessage'
        )
        self.assertEqual(backend, mock_backend_instance)

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID='mock')
    def test_make_backend_instance__custom_backend(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'custom'
        mock_backend_instance = mock.MagicMock()
        mock_backend_class.return_value = mock_backend_instance
        registry.add(mock_backend_class)
        backend = registry.make_backend_instance(
            phone_number='12345678',
            message='Testmessage',
            backend_id='custom'
        )
        mock_backend_class.assert_called_once_with(
            phone_number='12345678',
            message='Testmessage'
        )
        self.assertEqual(backend, mock_backend_instance)

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID='mock')
    def test_send__default_backend(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'mock'
        mock_backend_instance = mock.MagicMock()
        mock_backend_class.return_value = mock_backend_instance
        registry.add(mock_backend_class)
        registry.send(
            phone_number='12345678',
            message='Testmessage'
        )
        mock_backend_class.assert_called_once_with(
            phone_number='12345678',
            message='Testmessage'
        )
        mock_backend_instance.send.assert_called_once_with()

    @test.override_settings(IEVV_SMS_DEFAULT_BACKEND_ID='mock')
    def test_send__custom_backend(self):
        registry = sms_registry.MockableRegistry()
        mock_backend_class = mock.MagicMock()
        mock_backend_class.get_backend_id.return_value = 'custom'
        mock_backend_instance = mock.MagicMock()
        mock_backend_class.return_value = mock_backend_instance
        registry.add(mock_backend_class)
        registry.send(
            phone_number='12345678',
            message='Testmessage',
            backend_id='custom'
        )
        mock_backend_class.assert_called_once_with(
            phone_number='12345678',
            message='Testmessage'
        )
        mock_backend_instance.send.assert_called_once_with()
