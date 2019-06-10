from datetime import datetime
from unittest.mock import Mock

from django.test import TestCase, override_settings
from rest_framework import status

from chibi_user.middleware.metric import User_for_api


@override_settings( ROOT_URLCONF='chibi_user.tests' )
class metric( TestCase ):

    def test_save_start_time( self ):
        request = Mock()
        get_response = Mock()
        middleware = User_for_api( get_response=get_response )
        middleware( request )
        self.assertTrue( hasattr( request, '_start_time' ) )
        self.assertIsInstance( request._start_time, datetime )
        return middleware, request

    def test_check_for_request_anonymous( self ):
        middleware, request = self.test_save_start_time()
        del request.user
        metrics = {}
        middleware.set_user_to_metrics( request, metrics )
        self.assertTrue( metrics[ 'is_anonymous' ] )

    def test_check_for_request_with_user( self ):
        middleware, request = self.test_save_start_time()
        request.user = Mock()
        metrics = {}
        middleware.set_user_to_metrics( request, metrics )
        self.assertFalse( metrics[ 'is_anonymous' ] )
        self.assertIn( 'user_pk', metrics )
        self.assertEqual( metrics[ 'user_pk' ], request.user.pk )

    def test_no_error_for_the_user( self ):
        middleware, request = self.test_save_start_time()
        request.user = Mock()
        response = Mock()
        response.status_code = status.HTTP_404_NOT_FOUND
        metrics = {}
        middleware.get_url_name_from_response = Mock()
        middleware.get_url_name_from_response.return_value = 'some_name'
        middleware.is_an_error_from_user( request, response, metrics )
        self.assertFalse( metrics[ 'user_error' ] )

    def test_error_for_the_user( self ):
        middleware, request = self.test_save_start_time()
        request.user = Mock()
        response = Mock()
        response.status_code = status.HTTP_404_NOT_FOUND
        metrics = {}
        middleware.get_url_name_from_response = Mock()
        middleware.get_url_name_from_response.return_value = 'some_name-detail'
        middleware.is_an_error_from_user( request, response, metrics )
        self.assertTrue( metrics[ 'user_error' ] )
