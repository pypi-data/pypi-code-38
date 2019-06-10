from unittest import TestCase
from chibi.snippet import is_type

class Test_is_type(TestCase):

    def setUp( self ):
        pass

    def test_is_iter_list( self ):
        self.assertTrue( is_type.is_iter( [ 1, 2, 3 ] ) )
        self.assertTrue( is_type.is_iter( [] ) )
        self.assertTrue( is_type.is_iter( list() ) )

    def test_is_iter_tuple( self ):
        self.assertTrue( is_type.is_iter( ( 1, 2, 3 ) ) )
        self.assertTrue( is_type.is_iter( tuple() ) )

    def test_is_iter_dict( self ):
        self.assertTrue( is_type.is_iter( { 'foo': 1 } ) )
        self.assertTrue( is_type.is_iter( dict() ) )

    def test_is_iter_string( self ):
        self.assertTrue( is_type.is_iter( "foo" ) )
        self.assertTrue( is_type.is_iter( "" ) )
