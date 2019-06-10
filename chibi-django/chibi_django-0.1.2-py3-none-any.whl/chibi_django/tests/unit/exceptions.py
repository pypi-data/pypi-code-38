import unittest
from chibi_django.exceptions import (
    Http_error, Http_internal_server_error, Http_bad_request, Http_not_found,
    generic_exception_handler )


class Test_generic_exception_handler( unittest.TestCase ):
    def test_should_solve_the_exception_http_error( self ):
        response = generic_exception_handler( Http_error(), None )
        self.assertTrue( response )
        self.assertEqual( response.data[ 'detail' ], 'Unhandled error.' )

    def test_should_solve_the_exception_http_internal_error( self ):
        response = generic_exception_handler(
            Http_internal_server_error(), None )
        self.assertTrue( response )
        self.assertEqual( response.data[ 'detail' ], 'Unhandled error.' )

    def test_should_solve_the_exception_http_bad_request( self ):
        response = generic_exception_handler( Http_bad_request(), None )
        self.assertTrue( response )
        self.assertEqual( response.data[ 'detail' ], 'Unhandled parameters.' )

    def test_should_solve_the_exception_http_not_found( self ):
        response = generic_exception_handler( Http_not_found(), None )
        self.assertTrue( response )
        self.assertEqual( response.data[ 'detail' ], 'Not found.' )
