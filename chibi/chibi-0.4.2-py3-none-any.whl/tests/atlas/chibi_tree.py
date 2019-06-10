from unittest import TestCase
import copy
from chibi.atlas.tree import Chibi_tree, build_tree


class Value_test:
    def __init__( self, *children ):
        self.children = list( children )

    def __repr__( self ):
        return str( id( self ) )


class Test_build_tree( TestCase ):
    def setUp( self ):
        self.level_1 = [
            Value_test(), Value_test(), Value_test()
        ]

        self.level_2 = [
            Value_test( Value_test() ),
            Value_test( Value_test(), Value_test() ), Value_test()
        ]

        self.level_3 = [
            Value_test( Value_test( Value_test() ) ),
            Value_test(
                Value_test(), Value_test( *self.level_1 ) ),
            Value_test()
        ]

        a = Value_test()
        self.level_4 = [
            a, Value_test( a ), Value_test( a ),
            Value_test()
        ]

        self.child_funtion = lambda o: o.children
        self.key_funtion = lambda o: o

    def test_work_with_level_1( self ):
        result = build_tree(
            *self.level_1, key=self.key_funtion, children=self.child_funtion )
        self.assertIsInstance( result, Chibi_tree )
        self.assertEqual( len( result ), 3 )
        for r in result.values():
            self.assertEqual( len( r ), 0 )

    def test_work_with_level_2( self ):
        result = build_tree(
            *self.level_2, key=self.key_funtion, children=self.child_funtion )
        self.assertIsInstance( result, Chibi_tree )
        self.assertEqual( len( result ), 3 )
        self.assertIn(
            self.level_2[0].children[0], result[ self.level_2[0] ] )
        self.assertIn(
            self.level_2[1].children[0], result[ self.level_2[1] ] )
        self.assertIn(
            self.level_2[1].children[1], result[ self.level_2[1] ] )

        self.assertFalse( result[ self.level_2[2] ] )

    def test_work_with_level_3( self ):
        result = build_tree(
            *self.level_3, key=self.key_funtion, children=self.child_funtion )

        result_level_1 = build_tree(
            *self.level_1, key=self.key_funtion, children=self.child_funtion )
        self.assertIsInstance( result, Chibi_tree )
        self.assertEqual( len( result ), 3 )
        self.assertIn(
            self.level_3[0].children[0], result[ self.level_3[0] ] )
        self.assertIn(
            self.level_3[0].children[0].children[0],
            result[ self.level_3[0] ][ self.level_3[0].children[0] ] )

        self.assertEqual(
            result_level_1,
            result[ self.level_3[1] ][ self.level_3[1].children[1] ] )

    def test_work_with_level_3_if_be_proccess_later_level_1( self ):
        result = build_tree(
            *self.level_3, key=self.key_funtion, children=self.child_funtion )
        result_origin = build_tree(
            *self.level_3, key=self.key_funtion, children=self.child_funtion )

        result_with_level_1 = build_tree(
            *self.level_1, key=self.key_funtion, children=self.child_funtion,
            results=result )

        self.assertEqual( result_origin, result_with_level_1 )

    def test_work_with_level_4( self ):
        result = build_tree(
            *self.level_4, key=self.key_funtion, children=self.child_funtion )

        self.assertEqual(
            result[ self.level_4[1] ][ self.level_4[1].children[0] ],
            result[ self.level_4[0] ] )

        self.assertEqual(
            result[ self.level_4[1] ][ self.level_4[1].children[0] ],
            result[ self.level_4[2] ][ self.level_4[2].children[0] ] )


class Test_flip_tree( TestCase ):
    def setUp( self ):
        self.level_1 = [
            Value_test(), Value_test(), Value_test()
        ]

        self.level_3 = [
            Value_test( Value_test( Value_test() ) ),
            Value_test(
                Value_test(), Value_test( *self.level_1 ) ),
            Value_test()
        ]

        self.child_funtion = lambda o: o.children
        self.key_funtion = lambda o: o

    def test_work_with_level_4( self ):
        result = build_tree(
            *self.level_3, key=self.key_funtion, children=self.child_funtion )

        l = self.level_3
        batches = result.dependencies_batches()
        self.assertIn( l[0].children[0].children[0], batches[0] )
        self.assertIn( l[1].children[1].children[0], batches[0] )
        self.assertIn( l[1].children[1].children[1], batches[0] )
        self.assertIn( l[1].children[1].children[2], batches[0] )
        self.assertIn( l[2], batches[0] )

        self.assertIn( l[1].children[0], batches[0] )

        self.assertIn( l[0].children[0], batches[1] )
        self.assertIn( l[1].children[1], batches[1] )

        self.assertIn( l[0], batches[2] )
        self.assertIn( l[1], batches[2] )
