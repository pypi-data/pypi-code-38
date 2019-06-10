from django.test import TestCase, override_settings
from django.utils import six
from rest_framework import status
from rest_framework.test import APIClient

from chibi_user.models import Token
from chibi_user.tests import get_user_test


class BaseTokenAuthTests( object ):
    """Token authentication"""
    model = None
    url_name = '/token/'
    header_prefix = 'Token '

    def setUp( self ):
        self.csrf_client = APIClient( enforce_csrf_checks=True )
        self.user, self.token = get_user_test()
        self.username = self.user.username
        self.key = self.token.key
        # self.path = reverse( self.url_name )

    def test_post_form_passing_token_auth( self ):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key
        response = self.csrf_client.post(
            self.path, { 'example': 'example' }, HTTP_AUTHORIZATION=auth
        )
        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_fail_post_form_passing_nonexistent_token_auth( self ):
        # use a nonexistent token key
        auth = self.header_prefix + 'wxyz6789'
        response = self.csrf_client.post(
            self.path, { 'example': 'example' }, HTTP_AUTHORIZATION=auth
        )
        self.assertEqual( response.status_code, status.HTTP_401_UNAUTHORIZED )

    def test_fail_post_form_passing_invalid_token_auth( self ):
        # add an 'invalid' unicode character
        auth = self.header_prefix + self.key + "¸"
        response = self.csrf_client.post(
            self.path, { 'example': 'example' }, HTTP_AUTHORIZATION=auth
        )
        self.assertEqual( response.status_code, status.HTTP_401_UNAUTHORIZED )

    def test_post_json_passing_token_auth( self ):
        """
        Ensure POSTing form over token auth with correct
        credentials passes and does not require CSRF
        """
        auth = self.header_prefix + self.key
        response = self.csrf_client.post(
            self.path, { 'example': 'example' },
            format='json', HTTP_AUTHORIZATION=auth
        )
        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_post_json_makes_one_db_query( self ):
        """
        Ensure that authenticating a user using a
        token performs only one DB query
        """
        auth = self.header_prefix + self.key

        def func_to_test():
            return self.csrf_client.post(
                self.path, { 'example': 'example' },
                format='json', HTTP_AUTHORIZATION=auth
            )

        self.assertNumQueries( 1, func_to_test )

    def test_post_form_failing_token_auth( self ):
        """
        Ensure POSTing form over token auth without correct credentials fails
        """
        response = self.csrf_client.post( self.path, { 'example': 'example' } )
        self.assertEqual( response.status_code, status.HTTP_401_UNAUTHORIZED )

    def test_post_json_failing_token_auth( self ):
        """
        Ensure POSTing json over token auth without correct credentials fails
        """
        response = self.csrf_client.post(
            self.path, {'example': 'example'}, format='json'
        )
        self.assertEqual( response.status_code, status.HTTP_401_UNAUTHORIZED )


@override_settings( ROOT_URLCONF='chibi_user.tests' )
class TokenAuthTests( BaseTokenAuthTests, TestCase ):
    model = Token
    path = '/token/'

    def test_token_has_auto_assigned_key_if_none_provided( self ):
        """Ensure creating a token with no key will auto-assign a key"""
        self.token.delete()
        token = self.model.objects.create( user=self.user )
        self.assertTrue( bool( token.key ))

    def test_generate_key_returns_string( self ):
        """Ensure generate_key returns a string"""
        token = self.model()
        key = token.generate_key()
        self.assertIsInstance( key, six.string_types )
