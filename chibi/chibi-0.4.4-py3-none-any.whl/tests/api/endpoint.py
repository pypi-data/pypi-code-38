import json

from vcr_unittest import VCRTestCase

from chibi.api import Endpoint
from chibi.atlas import Chibi_atlas


class Endpoint_test( Endpoint ):
    url = 'http://a.4cdn.org/{board}/threads.json'


class Test_endpoint_4chan_wallpaper_board( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint( 'http://a.4cdn.org/w/threads.json' )


class Test_endpoint_4chan_thread( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint( 'http://a.4cdn.org/{board}/threads.json' )
        pass


class Test_endpoint_class( VCRTestCase ):
    def setUp( self ):
        self.endpoint = Endpoint_test()


class Test_get( Test_endpoint_4chan_wallpaper_board ):
    def test_response_should_be_200( self ):
        response = self.endpoint.get()
        self.assertEqual( response.status_code, 200 )
        self.assertIsInstance( response.headers, Chibi_atlas )
        self.assertIsInstance( response.body, str )
        self.assertIsInstance( response.native, list )
        self.assertListEqual( json.loads( response.body ), response.native )


class Test_init:
    def test_the_url_in_the_insntace_should_no_be_none( self ):
        self.assertIsNotNone( self.endpoint.assigned_url )


class Test_format:
    def test_should_create_another_instance_of_endpoint( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertIsNot( new_endpoint, self.endpoint )

    def test_should_change_the_url( self ):
        new_endpoint = self.endpoint.format( board='w' )
        self.assertEqual(
            new_endpoint.format_url, 'http://a.4cdn.org/w/threads.json' )


class Test_instance( Test_endpoint_4chan_thread, Test_format, Test_init ):
    pass


class Test_format_class( Test_endpoint_class, Test_format, Test_init ):
    pass
