from django.test import TestCase
from faker import Factory as Faker_factory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from chibi_user.models import Token
from chibi_user.tests import get_user_test, get_superuser_test
from test_runners.snippet.response import get_location, assert_status_code


fake = Faker_factory.create()


class Test_views_normal_user( TestCase ):
    model = Token
    path = '/token/'

    def setUp( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        self.super_user, self.super_token  = get_superuser_test()
        self.user, self.user_token = get_user_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.user_token ) )

    def test_fail_with_normal_user( self ):
        response = self.client.get(
            '/users/', HTTP_AUTHORIZATION=str( self.user_token ) )

        assert_status_code( response, status.HTTP_403_FORBIDDEN )


class Test_views( TestCase ):
    model = Token
    path = '/token/'

    def setUp( self ):
        self.client = APIClient( enforce_csrf_checks=True )
        self.super_user, self.super_token  = get_superuser_test()
        self.user, self.user_token = get_superuser_test()
        self.client.credentials( HTTP_AUTHORIZATION=str( self.user_token ) )

    def test_access_with_super_user( self ):
        auth = str( self.super_token )
        response = self.client.get( '/users/',
                                    HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_200_OK )

    def test_create_user( self ):
        auth = str( self.super_token )
        response = self.client.post(
            '/users/', HTTP_AUTHORIZATION=auth,
            data={
                'first_name': fake.first_name(),
                'last_name': fake.last_name(), 'email': fake.email(),
                'username': fake.user_name(),
            } )

        self.assertEqual( response.status_code, status.HTTP_201_CREATED,
                          ( "the status code should be 200 instead "
                            "of {}\ndata:{}" ).format( response.status_code,
                                                       response.data ) )
        assert_status_code( response, status.HTTP_201_CREATED )
        response = get_location( response, client=self.client )

        self.assertIsInstance( response.data[ 'pk' ], str )
        self.assertIn( 'token', response.data )
        self.assertIn( 'key', response.data[ 'token' ] )
        self.assertIsInstance( response.data[ 'token' ][ 'key' ], str )
        return response.data

    def test_delete_user( self ):
        data = self.test_create_user()
        auth = str( self.super_token )
        url = reverse( 'users:users-detail', kwargs={ 'pk': data[ 'pk' ] } )
        response = self.client.delete( url, HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_204_NO_CONTENT )

    def test_refresh_token( self ):
        data = self.test_create_user()
        auth = str( self.super_token )
        url = reverse(
            'users:users-refresh-token', kwargs={ 'pk': data[ 'pk' ] } )
        response = self.client.post( url, HTTP_AUTHORIZATION=auth )

        self.assertEqual( response.status_code, status.HTTP_200_OK )
        self.assertNotEqual( data[ 'token' ][ 'key' ],
                             response.data[ 'key' ] )
