from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from test_runners.snippet.response import assert_status_code


class Test_status_code( APITestCase ):
    expected_status_code = status.HTTP_200_OK
    url_name = 'namespace:name'


class Test_list( Test_status_code ):
    def test_list( self ):
        url_kw = self.get_url_kw()
        url = reverse( self.url_name, kwargs=url_kw )
        response = self.client.get( url )
        assert_status_code( response, self.expected_status_code )

    def get_url_kw( self ):
        raise NotImplementedError


class Test_retrieve( Test_status_code ):
    def test_retrieve( self ):
        url_kw = self.get_url_kw()
        url = reverse( self.url_name, kwargs=url_kw )
        response = self.client.get( url )
        assert_status_code( response, self.expected_status_code )

    def get_url_kw( self ):
        raise NotImplementedError

    def get_post_data( self ):
        raise NotImplementedError


class Test_create( Test_status_code ):
    expected_status_code = status.HTTP_201_CREATED

    def test_create( self ):
        url_kw = self.get_url_kw()
        url = reverse( self.url_name, kwargs=url_kw )
        post_data = self.get_post_data()
        response = self.client.post( url, data=post_data )
        assert_status_code( response, self.expected_status_code )

    def get_url_kw( self ):
        raise NotImplementedError

    def get_post_data( self ):
        raise NotImplementedError
