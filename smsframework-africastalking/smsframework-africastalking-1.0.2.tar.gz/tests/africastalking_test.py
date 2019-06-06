import unittest

import requests_mock
from smsframework import Gateway, OutgoingMessage

from smsframework_africastalking import AfricasTalkingProvider
from smsframework_africastalking.error import AfricasTalkingProviderError, InvalidNumberError


def _mock_response(status_code, msg_response):
    """
    Decorator function to handle mocking responses to API calls

    :param status_code: (int) Mocked response status code
    :param msg_response: (dict) Mocked message response details
    """
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            response = {
                'SMSMessageData': {
                    'Recipients': [msg_response]
                }
            }
            with requests_mock.mock() as mocker:
                mocker.post(
                    'https://api.sandbox.africastalking.com/version1/messaging',
                    headers={'content-type': 'application/json'},
                    status_code=status_code,
                    json=response
                )
                test_func(*args, **kwargs)
        return wrapper
    return decorator


class AfricasTalkingProviderTest(unittest.TestCase):
    def setUp(self):
        """Initialize AfricasTalkingProvider"""
        self.gw = gw = Gateway()
        gw.add_provider(
            'africas_talking',
            AfricasTalkingProvider,
            username='sandbox',
            api_key='api_key'
        )

    @_mock_response(200, {'status': 'Success', 'messageId': '001'})
    def test_send_success(self):
        """Test a successful AfricasTalking SMS send"""
        message_out = OutgoingMessage(
            '+254789789789',
            'Hello Kenya',
            provider='africas_talking'
        ).params(
            target_country='KE'
        )
        message_back = self.gw.send(message_out)
        self.assertEqual(message_back.msgid, '001')

    @_mock_response(500, {'status': 'Failed'})
    def test_send_failure(self):
        """Test a failing AfricasTalking SMS send"""
        message_out = OutgoingMessage(
            '+254789789789',
            'Hello Kenya',
            provider='africas_talking'
        ).params(
            target_country='KE'
        )
        self.assertRaises(
            AfricasTalkingProviderError,
            self.gw.send,
            message_out
        )

    @_mock_response(403, {'status': 'InvalidPhoneNumber'})
    def test_bad_number_failure(self):
        """Test a failing AfricasTalking SMS send (bad phone number)"""
        message_out = OutgoingMessage(
            '+254789789789',
            'Hello Rwanda',
            provider='africas_talking'
        ).params(
            target_country='RW'
        )
        self.assertRaises(
            InvalidNumberError,
            self.gw.send,
            message_out
        )
