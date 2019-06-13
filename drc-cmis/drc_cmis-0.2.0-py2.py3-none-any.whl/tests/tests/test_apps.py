# from unittest.mock import patch
from django.test import TestCase, override_settings

from drc_cmis.apps import check_cmis


class CheckCMISTests(TestCase):
    def test_check_cmis(self):
        check_cmis('test')

    @override_settings(DRC_CMIS_CLIENT_USER_PASSWORD='Not correct')
    def test_no_correct_password(self):
        check_cmis('test')

    # @patch('drc_cmis.client.CmisClient')
    # def test_check_cmis_no_multifilling(self, client_mock):
    #     client_mock.return_value = 2
    #     check_cmis('test')
    #     print(dir(client_mock))
    #     self.assertTrue(client_mock.called)
