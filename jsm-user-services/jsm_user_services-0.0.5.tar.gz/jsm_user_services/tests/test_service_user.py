from unittest import mock

from django.test import TestCase
from jsm_user_services import local_threading
# from jsm_user_services.services.user import get_ltm_user_data_from_jwt
from jsm_user_services.services.user import current_jwt_token
from jsm_user_services.services.user import get_jsm_token
from jsm_user_services.services.user import get_jsm_user_data_from_jwt
from jsm_user_services.services.user import get_ltm_token
from jsm_user_services.services.user import get_user_email_from_jwt
from jsm_user_services.services.user import jwt_has_required_roles


class TestContracts(TestCase):
    def setUp(self):

        self.jwt = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTYxODAzNDAzLCJqdGkiOiI0MDJlYmJjNDdkNGE0NDUxYmRjZDIwMmQyYTEwOTdiMiIsInl1bnRpYW5kdSI6InhJRTVucGZ4d3l0dXZhQVlWRW5rdUxDclVhcWl0YW9xY09kMUZvZXJCT045TW5qdmNyQ3YzWXZnYXVibk9IMEVVR2swbkl6NmppTWNZdlphckJGZ2M4clVycVVjN3NKcGVfVWZieklPZjNldXlTbTZ3Wmc2SEpQU2d2dmN2akhNTnVTcVR6ZmduUzhUV3ZWNTYyQmI5UHFEUUZjODdUdS0zR0gzdEpJWTRZQ3NEYjRJRXFXLUJSVUJSYlpPRGZ6NnNLSkxGekZEaVRMa2djWGZ6MVJ6b1c5ZGtOYXVUWnZ5Wkk1dkhOeWJhTzRwLVlnWmJ0YkZXb1ktMWFCZ0x4MzFUeGdNUmxsYS1UZzBkU2dveGM1OTV2d3U5aDlnTUh3cGVVNU5DQ0gyS2g0NnZmNGExRlVzM3I5TjlWYUJzQlBFRkpwR2RhNkdzS0l2a1RKMHd5QTZLOUN3OUtJYS04Sy15bUFCUmdHWFVaSTN3LWMzdnB0Xzd2TkQzbFhEZC1CU0xVdWhubDd3VE92QnYxNGpjS1gweGR2MzJmRUdXam1WSnNIa3QxTDl2NG9PRmhmTWJJeEFoY2RLc1IyTUlDemVZZjh0ODJJZDhSMEZqNUJMV3BQVXM1VG5OQXV3UzJOcm1UQWtfT0psZUk1TGdBRlBjVEpXcWZDeDl5cDJab2FMT1FteGF6aEdCNHo5MnRBamFQYTVySEFaWTBibThBbVZvakxjVkIwMWVJeUVwN3dPY2VFRGI0UVRkdEtoREZFcGxOa1ZHakRQNTZLbDYzRThWTHpoemhXQllQRXdPd2RHS3FKT09Lek4wcDN1NWhtQWZJSTFHUHFHb0ZIaTNFbEpNRlB0TnhxN0R0LUo4VGpHSGo1NEc0QWRqUUVvNFpqdjBPNFBtS0R6SmRUeTNGM0JiQjZMU092czVfd0V1bkFlSkJqREFSOW1jQWdNcWxsbDVDRXJhNjc4cmQzMUE1Vm51MXl3WXFuLTlfUSIsImpzbV9pZGVudGl0eSI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUpsYldGcGJDSTZJakV5TXpRMVFHeHZlV0ZzZEhsS1UwMHVZMjl0SWl3aWRXNXBjWFZsWDI1aGJXVWlPaUpoYzJRaUxDSjNaV0p6YVhSbElqb2lRMnhwWlc1MFFYQndiR2xqWVhScGIyNGlMQ0oxYVdRaU9pSTROVEEzTVdSa1pTMWlOVFk0TFRReFlXWXRZVFUzT1MwelpqUXlZekZrWmpBNU9UZ2lMQ0p6Wld4c1pYSnpJanBiSWpGbE0ySTRNekZtTFRrMVpEQXROREZoTnkxaU0yVXhMVEZtWlRBelptRmxNakEwTmlJc0lqWTNaV1k0TXpBeUxXSTFORFl0TkRRMVlTMDVZV0l5TFRobU4yWTRPR0kyTWpBM09DSmRMQ0p5YjJ4bElqb2lRM1Z6ZEc5dFpYSWlMQ0pqYm5CcWN5STZJalk0TGpVNU55NHlPREF2TURBd01TMHdPU0lzSW01aVppSTZNVFUyTVRjek1UUXdNaXdpWlhod0lqb3hOVFl5TXpNMk1qQXlMQ0pwWVhRaU9qRTFOakUzTXpFME1ESXNJbWx6Y3lJNkluUm1jRG92TDJsa1pXNTBhWFI1TG1wemJTOWhkWFJvYjNKcGRIa2lMQ0poZFdRaU9pSmlZekExTVdSbE15MWhaV0ZoTFRSaFl6a3RPR1ppWmkwd05XRTRObVV3T0RObVkyWWlmUS5sRHpDdWFQeTJobDhJUDlFb3p0QmpwR2NLVkh5RVZLdVgxWUtMeUgxd0pBIn0.CzhdhYN6porjALfSktQvE9gIfK34BHibFOLjZ-BUAzw"

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

        token_jsm = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IjEyMzQ1QGxveWFsdHlKU00uY29tIiwidW5pcXVlX25hbWUiOiJhc2QiLCJ3ZWJzaXRlIjoiQ2xpZW50QXBwbGljYXRpb24iLCJ1aWQiOiI4NTA3MWRkZS1iNTY4LTQxYWYtYTU3OS0zZjQyYzFkZjA5OTgiLCJzZWxsZXJzIjpbIjFlM2I4MzFmLTk1ZDAtNDFhNy1iM2UxLTFmZTAzZmFlMjA0NiIsIjY3ZWY4MzAyLWI1NDYtNDQ1YS05YWIyLThmN2Y4OGI2MjA3OCJdLCJyb2xlIjoiQ3VzdG9tZXIiLCJjbnBqcyI6IjY4LjU5Ny4yODAvMDAwMS0wOSIsIm5iZiI6MTU2MTczMTQwMiwiZXhwIjoxNTYyMzM2MjAyLCJpYXQiOjE1NjE3MzE0MDIsImlzcyI6InRmcDovL2lkZW50aXR5LmpzbS9hdXRob3JpdHkiLCJhdWQiOiJiYzA1MWRlMy1hZWFhLTRhYzktOGZiZi0wNWE4NmUwODNmY2YifQ.lDzCuaPy2hl8IP9EoztBjpGcKVHyEVKuX1YKLyH1wJA"

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

        token_ltm = "xIE5npfxwytuvaAYVEnkuLCrUaqitaoqcOd1FoerBON9MnjvcrCv3YvgaubnOH0EUGk0nIz6jiMcYvZarBFgc8rUrqUc7sJpe_UfbzIOf3euySm6wZg6HJPSgvvcvjHMNuSqTzfgnS8TWvV562Bb9PqDQFc87Tu-3GH3tJIY4YCsDb4IEqW-BRUBRbZODfz6sKJLFzFDiTLkgcXfz1RzoW9dkNauTZvyZI5vHNybaO4p-YgZbtbFWoY-1aBgLx31TxgMRlla-Tg0dSgoxc595vwu9h9gMHwpeU5NCCH2Kh46vf4a1FUs3r9N9VaBsBPEFJpGda6GsKIvkTJ0wyA6K9Cw9KIa-8K-ymABRgGXUZI3w-c3vpt_7vND3lXDd-BSLUuhnl7wTOvBv14jcKX0xdv32fEGWjmVJsHkt1L9v4oOFhfMbIxAhcdKsR2MICzeYf8t82Id8R0Fj5BLWpPUs5TnNAuwS2NrmTAk_OJleI5LgAFPcTJWqfCx9yp2ZoaLOQmxazhGB4z92tAjaPa5rHAZY0bm8AmVojLcVB01eIyEp7wOceEDb4QTdtKhDFEplNkVGjDP56Kl63E8VLzhzhWBYPEwOwdGKqJOOKzN0p3u5hmAfII1GPqGoFHi3ElJMFPtNxq7Dt-J8TjGHj54G4AdjQEo4Zjv0O4PmKDzJdTy3F3BbB6LSOvs5_wEunAeJBjDAR9mcAgMqlll5CEra678rd31A5Vnu1ywYqn-9_Q"

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
            "email": "12345@loyaltyJSM.com",
            "unique_name": "asd",
            "website": "ClientApplication",
            "uid": "85071dde-b568-41af-a579-3f42c1df0998",
            "sellers": ["1e3b831f-95d0-41a7-b3e1-1fe03fae2046", "67ef8302-b546-445a-9ab2-8f7f88b62078"],
            "role": "Customer",
            "cnpjs": "68.597.280/0001-09",
            "nbf": 1561731402,
            "exp": 1562336202,
            "iat": 1561731402,
            "iss": "tfp://identity.jsm/authority",
            "aud": "bc051de3-aeaa-4ac9-8fbf-05a86e083fcf",
        }

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertIsNotNone(get_jsm_user_data_from_jwt())
        self.assertEqual(get_jsm_user_data_from_jwt(), data)

    # def test_get_ltm_user_data_from_jwt_should_return_none_when_local_threading_dont_have_key(self):
    #
    #     try:
    #         delattr(local_threading, "authorization_token")
    #     except:
    #         pass
    #
    #     self.assertIsNone(get_ltm_user_data_from_jwt())

    # def test_get_ltm_user_data_from_jwt_should_return_data_when_local_threading_have_key(self):
    #
    #     data = {
    #         "email": "12345@loyaltyJSM.com",
    #         "unique_name": "asd",
    #         "website": "ClientApplication",
    #         "uid": "85071dde-b568-41af-a579-3f42c1df0998",
    #         "sellers": ["1e3b831f-95d0-41a7-b3e1-1fe03fae2046", "67ef8302-b546-445a-9ab2-8f7f88b62078"],
    #         "role": "Customer",
    #         "cnpjs": "68.597.280/0001-09",
    #         "nbf": 1561731402,
    #         "exp": 1562336202,
    #         "iat": 1561731402,
    #         "iss": "tfp://identity.jsm/authority",
    #         "aud": "bc051de3-aeaa-4ac9-8fbf-05a86e083fcf",
    #     }
    #
    #     setattr(local_threading, "authorization_token", self.jwt)
    #
    #     self.assertIsNotNone(get_ltm_user_data_from_jwt())
    #     self.assertEqual(get_ltm_user_data_from_jwt(), data)

    def test_get_email_from_jwt_should_return_email_when_token_exists(self):

        setattr(local_threading, "authorization_token", self.jwt)

        self.assertEqual(get_user_email_from_jwt(), "12345@loyaltyJSM.com")

    @mock.patch("jsm_user_services.services.user.get_jsm_user_data_from_jwt")
    def test_jwt_has_required_roles_assert_all_true(self, mocked_get_jsm_user_data_from_jwt):
        mocked_get_jsm_user_data_from_jwt.return_value = {
            "iss": "Online JWT Builder",
            "iat": 1559177717,
            "exp": 1590713717,
            "aud": "www.example.com",
            "sub": "jrocket@example.com",
            "email": "1234567890@email.com",
            "roles": ["Dev", "Project Administrator"],
        }

        self.assertTrue(jwt_has_required_roles(["Dev", "Project Administrator"]))

    @mock.patch("jsm_user_services.services.user.get_jsm_user_data_from_jwt")
    def test_jwt_has_required_roles_assert_all_false(self, mocked_get_jsm_user_data_from_jwt):
        mocked_get_jsm_user_data_from_jwt.return_value = {
            "iss": "Online JWT Builder",
            "iat": 1559177717,
            "exp": 1590713717,
            "aud": "www.example.com",
            "sub": "jrocket@example.com",
            "email": "1234567890@email.com",
            "roles": ["Dev", "Project Administrator"],
        }

        self.assertFalse(jwt_has_required_roles(["Dev"]))

    @mock.patch("jsm_user_services.services.user.get_jsm_user_data_from_jwt")
    def test_jwt_has_required_roles_assert_any_true(self, mocked_get_jsm_user_data_from_jwt):
        mocked_get_jsm_user_data_from_jwt.return_value = {
            "iss": "Online JWT Builder",
            "iat": 1559177717,
            "exp": 1590713717,
            "aud": "www.example.com",
            "sub": "jrocket@example.com",
            "email": "1234567890@email.com",
            "roles": ["Dev", "Project Administrator"],
        }

        self.assertTrue(jwt_has_required_roles(["Dev"], assert_all=False))

    @mock.patch("jsm_user_services.services.user.get_jsm_user_data_from_jwt")
    def test_jwt_has_required_roles_assert_any_false(self, mocked_get_jsm_user_data_from_jwt):
        mocked_get_jsm_user_data_from_jwt.return_value = {
            "iss": "Online JWT Builder",
            "iat": 1559177717,
            "exp": 1590713717,
            "aud": "www.example.com",
            "sub": "jrocket@example.com",
            "email": "1234567890@email.com",
            "roles": ["Dev", "Project Administrator"],
        }

        self.assertFalse(jwt_has_required_roles(["X"], assert_all=False))
