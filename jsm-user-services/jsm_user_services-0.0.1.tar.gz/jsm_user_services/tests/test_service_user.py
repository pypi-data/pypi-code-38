from django.test import TestCase
from jsm_user_services import local_threading
from jsm_user_services.services.user import current_jwt_token
from jsm_user_services.services.user import get_jsm_token
from jsm_user_services.services.user import get_jsm_user_data_from_jwt
from jsm_user_services.services.user import get_ltm_token
from jsm_user_services.services.user import get_ltm_user_data_from_jwt
from jsm_user_services.services.user import get_user_email_from_jwt


class TestContracts(TestCase):
    def setUp(self):

        self.jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE1NTkxNzc3MTcsImV4cCI6MTU5MDcxMzcxNywiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoiMTIzNDU2Nzg5MEBlbWFpbC5jb20iLCJlbWFpbCI6IjEyMzQ1Njc4OTBAZW1haWwuY29tIiwianNtX2lkZW50aXR5IjoiZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnBjM01pT2lKUGJteHBibVVnU2xkVUlFSjFhV3hrWlhJaUxDSnBZWFFpT2pFMU5Ua3hOemMzTVRjc0ltVjRjQ0k2TVRVNU1EY3hNemN4Tnl3aVlYVmtJam9pZDNkM0xtVjRZVzF3YkdVdVkyOXRJaXdpYzNWaUlqb2lhbkp2WTJ0bGRFQmxlR0Z0Y0d4bExtTnZiU0lzSW1WdFlXbHNJam9pTVRJek5EVTJOemc1TUVCbGJXRnBiQzVqYjIwaUxDSnliMnhsY3lJNld5SkVaWFlpTENKUWNtOXFaV04wSUVGa2JXbHVhWE4wY21GMGIzSWlYWDAuck5aMndtdTdpYzc3WWR6eFpUNzRnUzlPdDNhbkJWSERNNklvUHdBN2tQYyIsInl1bnRpYW5kdSI6ImV5SjBlWEFpT2lKS1YxUWlMQ0poYkdjaU9pSklVekkxTmlKOS5leUpwYzNNaU9pSlBibXhwYm1VZ1NsZFVJRUoxYVd4a1pYSWlMQ0pwWVhRaU9qRTFOVGt4TmprME16UXNJbVY0Y0NJNk1UVTVNRGN3TlRRek5Dd2lZWFZrSWpvaWQzZDNMbVY0WVcxd2JHVXVZMjl0SWl3aWMzVmlJam9pTVRJek5EVTJOemc1TUVCbGJXRnBiQzVqYjIwaUxDSm1hWEp6ZEU1aGJXVWlPaUptYVhKemRGOXVZVzFsSWl3aVUzVnlibUZ0WlNJNklteGhjM1JmYm1GdFpTSXNJa1Z0WVdsc0lqb2lNVEl6TkRVMk56ZzVNRUJsYldGcGJDNWpiMjBpTENKU2IyeGxJanBiSWtSbGRpSXNJbEJ5YjJwbFkzUWdRV1J0YVc1cGMzUnlZWFJ2Y2lKZGZRLnVUbjU2cW1WTHlETTJYRURYZDU3OXJYY3lrNm1fSHNvM2x0TG9Wd0Q5TGcifQ.qsTfBbaDOAxKJbfR0rJ5nlr9wt4hZzJPco4mjnusu7E"

    def test_current_jwt_token_should_return_none_when_local_threading_dont_have_key(self):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        self.assertIsNone(current_jwt_token())

    def test_current_jwt_token_should_return_none_when_local_threading_have_key(self):

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(current_jwt_token())
        self.assertEqual(current_jwt_token(), self.jwt)

    def test_get_jsm_token_should_return_none_when_current_jwt_token_return_none(self):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        self.assertIsNone(get_jsm_token())

    def test_get_jsm_token_should_return_token_when_current_jwt_token_have_token(self):

        token_jsm = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE1NTkxNzc3MTcsImV4cCI6MTU5MDcxMzcxNywiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoianJvY2tldEBleGFtcGxlLmNvbSIsImVtYWlsIjoiMTIzNDU2Nzg5MEBlbWFpbC5jb20iLCJyb2xlcyI6WyJEZXYiLCJQcm9qZWN0IEFkbWluaXN0cmF0b3IiXX0.rNZ2wmu7ic77YdzxZT74gS9Ot3anBVHDM6IoPwA7kPc"

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(get_jsm_token())
        self.assertEqual(get_jsm_token(), token_jsm)

    def test_get_ltm_token_should_return_none_when_current_jwt_token_return_none(self):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        self.assertIsNone(get_ltm_token())

    def test_get_ltm_token_token_should_return_token_when_current_jwt_token_have_token(self):

        token_ltm = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE1NTkxNjk0MzQsImV4cCI6MTU5MDcwNTQzNCwiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoiMTIzNDU2Nzg5MEBlbWFpbC5jb20iLCJmaXJzdE5hbWUiOiJmaXJzdF9uYW1lIiwiU3VybmFtZSI6Imxhc3RfbmFtZSIsIkVtYWlsIjoiMTIzNDU2Nzg5MEBlbWFpbC5jb20iLCJSb2xlIjpbIkRldiIsIlByb2plY3QgQWRtaW5pc3RyYXRvciJdfQ.uTn56qmVLyDM2XEDXd579rXcyk6m_Hso3ltLoVwD9Lg"

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(get_ltm_token())
        self.assertEqual(get_ltm_token(), token_ltm)

    def test_get_jsm_user_data_from_jwt_should_return_none_when_local_threading_dont_have_key(self):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        self.assertIsNone(get_jsm_user_data_from_jwt())

    def test_get_jsm_user_data_from_jwt_should_return_data_when_local_threading_have_key(self):

        data = {
            "iss": "Online JWT Builder",
            "iat": 1559177717,
            "exp": 1590713717,
            "aud": "www.example.com",
            "sub": "jrocket@example.com",
            "email": "1234567890@email.com",
            "roles": ["Dev", "Project Administrator"],
        }

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(get_jsm_user_data_from_jwt())
        self.assertEqual(get_jsm_user_data_from_jwt(), data)

    def test_get_ltm_user_data_from_jwt_should_return_none_when_local_threading_dont_have_key(self):

        try:
            delattr(local_threading, "authorization_token")
        except:
            pass

        self.assertIsNone(get_ltm_user_data_from_jwt())

    def test_get_ltm_user_data_from_jwt_should_return_data_when_local_threading_have_key(self):

        data = {
            "iss": "Online JWT Builder",
            "iat": 1559169434,
            "exp": 1590705434,
            "aud": "www.example.com",
            "sub": "1234567890@email.com",
            "firstName": "first_name",
            "Surname": "last_name",
            "Email": "1234567890@email.com",
            "Role": ["Dev", "Project Administrator"],
        }

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(get_ltm_user_data_from_jwt())
        self.assertEqual(get_ltm_user_data_from_jwt(), data)

    def test_get_email_from_jwt_should_return_email_when_token_exists(self):

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertEqual(get_user_email_from_jwt(), "1234567890@email.com")
