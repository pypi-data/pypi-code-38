from unittest import TestCase
from chibi.api.connection import Connections


class Test_connection( TestCase ):
    def setUp( self ):
        self.connections = Connections()


class Test_connection_configure( Test_connection ):
    def test_should_start_empty( self ):
        self.assertIsNotNone( self.connections._connections )
        self.assertDictEqual( self.connections._connections, {} )


class Test_configure( Test_connection ):
    def setUp( self ):
        super().setUp()
        self.default_settings = { 'something': 'asdf' }
        self.connections.configure( default=self.default_settings )

    def test_get_should_retrive_default( self ):
        default = self.connections.get()
        self.assertEqual( default, self.default_settings )

    def test_get_item_should_retrive_by_key( self ):
        default = self.connections[ 'default' ]
        self.assertEqual( default, self.default_settings )

    def test_get_should_raise_key_error_when_is_no_exists_connection( self ):
        with self.assertRaises( KeyError ):
            self.connections.get( 'explotion' )

    def test_get_item_should_raise_key_error_when_is_no_find_key( self ):
        with self.assertRaises( KeyError ):
            self.connections[ 'explotion' ]
