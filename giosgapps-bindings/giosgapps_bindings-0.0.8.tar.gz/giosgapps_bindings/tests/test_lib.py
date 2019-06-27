from django.test import TestCase, RequestFactory
from ..django.utils import GiosgappTriggerContext
import jwt
import time

SIGN_KEY = '123abc456cde'


class GiosgTriggerAbstractionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Use old JWTs from test app, unpack them without validating signature since we sign the data again anyway
        # To-Consider: Building the sample JWTs from mere dictionary data set
        data_jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDAwZjcxMTYtNDQ5OS0xMWU5LWJjYTQtMDI0MmFjMTEwMDA5Iiwic3ViIjoic2VydmljZS5naW9zZy5jb20iLCJvcmdfaWQiOiJhMTdjZWE4MC1lMzk3LTExZTAtYjUxYS0wMDE2M2UwYzAxZjIiLCJhcHBfdXNlcl9jb2RlIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnZjbWRoYm1sNllYUnBiMjVmYVdRaU9pSmhNVGRqWldFNE1DMWxNemszTFRFeFpUQXRZalV4WVMwd01ERTJNMlV3WXpBeFpqSWlMQ0pxZEdraU9pSTRNMkl6T0dSbVlTMDFNak5tTFRFeFpUa3RPREExT0Mwd01qUXlZV014TVRBd01EZ2lMQ0poZFdRaU9sc2lhSFIwY0hNNkx5OXpaWEoyYVdObExtZHBiM05uTG1OdmJTOXBaR1Z1ZEdsMGVTOTBiMnRsYmlKZExDSmxlSEFpT2pFMU5UTTROelk0TmpVdU56VXhNVEV4TENKMWMyVnlYMmxrSWpvaU9ETTVPVFZoTlRJdE5USXpaaTB4TVdVNUxUZ3dOVGd0TURJME1tRmpNVEV3TURBNElpd2lhWE56SWpvaWFIUjBjSE02THk5elpYSjJhV05sTG1kcGIzTm5MbU52YlM5cFpHVnVkR2wwZVM5aGRYUm9iM0pwZW1VaUxDSnBZWFFpT2pFMU5UTTROelk0TXpVdU56VXhNVEVzSW1Gd2NGOXBaQ0k2SWpKa05ERTNaVEl5TFRSbVpEUXRNVEZsT1MwNU9USTRMVEF5TkRKaFl6RXhNREF3TlNKOS5PUlkta1FDLTNBNExyczFVMDBHMF9vblpPUlRia2tjY1dWRkZfUGdiTkFvIiwidmlzaXRvcl9pZCI6IiIsImFwcF9pZCI6IjJkNDE3ZTIyLTRmZDQtMTFlOS05OTI4LTAyNDJhYzExMDAwNSIsImluc3RfaWQiOiI4MzllZGE3Yy01MjNmLTExZTktODA1OC0wMjQyYWMxMTAwMDgiLCJhcHBfdXNlcl9pZCI6IjgzOTk1YTUyLTUyM2YtMTFlOS04MDU4LTAyNDJhYzExMDAwOCIsImNoYXRfaWQiOiIiLCJleHAiOjE1NTM4Nzc0MzUsInJvb21faWQiOm51bGwsIl9vcmdfaWQiOjEsImRvbWFpbl9ob3N0IjpudWxsLCJfdXNlcl9pZCI6Mjg4NDJ9.ST7ab1dvKuiKcsRI677o5CgK_t3Qrb4PLQNoXxy5T2U'
        access_token_jwt = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDAwZjcxMTYtNDQ5OS0xMWU5LWJjYTQtMDI0MmFjMTEwMDA5Iiwic3ViIjoic2VydmljZS5naW9zZy5jb20iLCJwZXJtcyI6W10sIm9yZ19pZCI6ImExN2NlYTgwLWUzOTctMTFlMC1iNTFhLTAwMTYzZTBjMDFmMiIsImFwcF9pZCI6IjJkNDE3ZTIyLTRmZDQtMTFlOS05OTI4LTAyNDJhYzExMDAwNSIsImluc3RfaWQiOiI4MzllZGE3Yy01MjNmLTExZTktODA1OC0wMjQyYWMxMTAwMDgiLCJleHAiOjE1NTM4Nzc0MzV9.Rj83FyBEXS_sTQxHgq_WDjhUD3C80e-5lw1MgyczNuo'
        data_content = jwt.decode(data_jwt, verify=False)
        access_token_content = jwt.decode(access_token_jwt, verify=False)
        # Create valid JWTs
        data_content['exp'] = int(time.time()) + 60*10  # Expiration in 10 minutes since set-up of TestCase
        access_token_content['exp'] = int(time.time()) + 60*10
        cls.VALID_DATA_JWT = jwt.encode(data_content, SIGN_KEY, algorithm='HS256')
        cls.VALID_TOKEN_JWT = jwt.encode(access_token_content, SIGN_KEY, algorithm='HS256')
        # Create forged (invalid signing key) data-JWT, access token JWT is not signed
        cls.FORGED_DATA_JWT = jwt.encode(data_content, 'fake_key_lol', algorithm='HS256')
        # Create expired JWTs, access token JWT is not checked -- we explicitly use data-JWT for authorization
        data_content['exp'] = int(time.time()) - 60*10
        cls.EXPIRED_DATA_JWT = jwt.encode(data_content, SIGN_KEY, algorithm='HS256')

    def test_missing_trigger_type(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            # Missing param 'type'
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('type' in str(e))

    def test_missing_data_jwt(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            # Missing param 'data'
            'token': self.VALID_TOKEN_JWT
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('data' in str(e))

    def test_invalid_signature_in_data_jwt(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.FORGED_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('signature' in str(e))

    def test_expired_signature_in_data_jwt(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.EXPIRED_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('expired' in str(e))

    def test_missing_install_redirect_uri(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'install',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
            # Missing 'redirect_uri' when type is 'install'
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('redirect_uri' in str(e))

    def test_missing_token_when_not_uninstall(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT
            # Missing param 'token'
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('token' in str(e))

    def test_accessible_properties(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        trigger = GiosgappTriggerContext(request, SIGN_KEY)

        # Check attrs exist
        self.assertTrue(hasattr(trigger, 'type'))
        self.assertTrue(hasattr(trigger, 'user_id'))
        self.assertTrue(hasattr(trigger, 'org_id'))
        self.assertTrue(hasattr(trigger, 'chat_id'))
        self.assertTrue(hasattr(trigger, 'visitor_id'))
        self.assertTrue(hasattr(trigger, 'inst_id'))
        self.assertTrue(hasattr(trigger, 'app_id'))
        self.assertTrue(hasattr(trigger, 'app_user_id'))
        self.assertTrue(hasattr(trigger, 'redirect_uri'))
        self.assertTrue(hasattr(trigger, 'access_token'))
        self.assertTrue(hasattr(trigger, 'access_token_exp'))

        # Check attrs are correctly typed
        self.assertTrue(isinstance(trigger.type, str))
        self.assertTrue(isinstance(trigger.user_id, str) or trigger.user_id is None)
        self.assertTrue(isinstance(trigger.org_id, str))
        self.assertTrue(isinstance(trigger.chat_id, str) or trigger.chat_id is None)
        self.assertTrue(isinstance(trigger.visitor_id, str) or trigger.visitor_id is None)
        self.assertTrue(isinstance(trigger.inst_id, str))
        self.assertTrue(isinstance(trigger.app_id, str))
        self.assertTrue(isinstance(trigger.app_user_id, str) or trigger.app_user_id is None)
        self.assertTrue(isinstance(trigger.redirect_uri, str) or trigger.redirect_uri is None)
        self.assertTrue(isinstance(trigger.access_token, str) or trigger.access_token is None)
        self.assertTrue(isinstance(trigger.access_token_exp, int) or trigger.access_token_exp is None)

    def test_authorization_header_content_getter(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        trigger = GiosgappTriggerContext(request, SIGN_KEY)
        self.assertTrue(isinstance(trigger.get_auth_header_content(), str))

    def test_auth_header_content_getter_unavailable_if_uninstall(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        try:
            trigger = GiosgappTriggerContext(request, SIGN_KEY)
            trigger.get_auth_header_content()
        except ValueError as e:
            self.assertTrue('token' in str(e))

    def test_persistent_token_exchanger_when_no_bot_user(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        trigger = GiosgappTriggerContext(request, SIGN_KEY)
        trigger.app_user_id = None
        try:
            trigger.exchange_persistent_access_token()
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('bot' in str(e).lower())  # Indicator of "missing bot user something something"

    def test_persistent_token_exchanger_when_expired_token(self):
        factory = RequestFactory()
        request = factory.get('/', data={
            'type': 'setup',
            'data': self.VALID_DATA_JWT,
            'token': self.VALID_TOKEN_JWT
        })
        trigger = GiosgappTriggerContext(request, SIGN_KEY)
        try:
            trigger.exchange_persistent_access_token()
            # Should go to the exception instead
            self.fail()
        except ValueError as e:
            self.assertTrue('expired' in str(e).lower())  # Indicator of "token expired something something"
