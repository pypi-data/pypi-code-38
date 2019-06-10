from unittest import TestCase
from chibi.api import Client
from chibi.api.connection import Connections


class Test_client( TestCase ):
    def setUp( self ):
        self.client = Client()


class Test_default_client( Test_client ):
    def test_should_using_the_default_connection( self ):
        self.assertEqual( self.client._default_connection_name, 'default' )


class Test_using( Test_client ):
    def test_using_should_generate_another_instnace( self ):
        self.client._connections.configure( default={} )
        new_client = self.client.using( 'default' )
        self.assertIsNot( new_client, self.client )

    def test_if_the_connection_no_exists_should_raise_a_key_error( self ):
        with self.assertRaises( KeyError ):
            self.client.using( 'explotion' )


class Test_extract_connections( Test_client ):
    def test_should_return_a_instance_of_connetions( self ):
        connections = self.client.extract_connections()
        self.assertIsInstance( connections, Connections )
