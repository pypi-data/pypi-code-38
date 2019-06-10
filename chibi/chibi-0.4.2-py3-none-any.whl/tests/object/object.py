from unittest import TestCase

from chibi.object import Chibi_object
from chibi.object.descriptor import (
    String, Dict, Tree_simple, Dict_defaults, Set
)


class Chibi_object_empty( Chibi_object ):
    pass


class Chibi_object_with_descriptors( Chibi_object ):
    name = String()
    test_dict = Dict()
    test_dict_default = Dict_defaults()
    test_tree = Tree_simple()
    test_set = Set()


class Chibi_object_with_defaults( Chibi_object ):
    name = String( default='hello' )
    test_dict_default = Dict_defaults( default='word' )


class Test_chibi_object( TestCase ):

    def test_chibi_object_simple( self ):
        obj = Chibi_object_empty()
        self.assertIsInstance( obj, Chibi_object )

    def test_with_descriptors( self ):
        obj = Chibi_object_with_descriptors()
        self.assertIsInstance( obj, Chibi_object )
        self.assertEqual( obj.name, '' )

        obj.name = 'hellooo'
        self.assertEqual( obj.name, 'hellooo' )
        self.assertIsNone( obj.test_dict )
        obj.test_dict = { 'key': 'test' }
        self.assertEqual( obj.test_dict, { 'key': 'test' } )

        self.assertFalse( obj.test_dict_default )
        data = obj.test_dict_default[ 'sadf' ]
        self.assertIsNone( data )

        self.assertFalse( obj.test_tree )
        self.assertEqual( list( obj.test_tree.keys() ), [] )

        self.assertEqual( len( obj.test_set ), 0 )

    def test_with_descriptior_assing( self ):
        obj = Chibi_object_with_descriptors( name='stuff', test_dict={} )
        self.assertEqual( obj.test_dict, {} )
        self.assertEqual( obj.name, 'stuff' )
        obj.name = 'asdf'
        self.assertEqual( obj.name, 'asdf' )
        obj.test_dict['asdf'] = 123
        self.assertEqual( obj.test_dict, { 'asdf': 123 } )

        self.assertFalse( obj.test_tree )
        obj.test_tree.a.b.c
        self.assertEqual( obj.test_tree, { 'a': { 'b': { 'c': {} } } } )
        obj.test_tree.a.rusky = 'RUSH B'
        self.assertEqual( obj.test_tree, { 'a': { 'rusky': 'RUSH B',
                                                  'b': { 'c': {} } } } )

        obj.test_dict_default[ 'qwer' ] = 'word'
        self.assertIsNotNone( obj.test_dict_default[ 'qwer' ] )
        self.assertEqual( obj.test_dict_default[ 'qwer' ], 'word' )

        obj.test_set |= set( 'abc' )
        self.assertEqual( len( obj.test_set ), 3 )

    def test_with_defaults( self ):
        obj = Chibi_object_with_defaults()
        self.assertEqual( obj.name, 'hello' )
        obj.name = 'zxcv'
        self.assertEqual( obj.name, 'zxcv' )

        word = obj.test_dict_default[ 'hello' ]
        self.assertEqual( word, 'word' )
