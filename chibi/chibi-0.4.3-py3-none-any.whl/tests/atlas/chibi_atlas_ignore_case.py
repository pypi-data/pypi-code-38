from unittest import TestCase
from chibi.atlas import Chibi_atlas_ignore_case



class Test_ignore_case:
    def test_can_retrive_upperkeys_and_are_equal_to_lower( self ):
        self.assertEqual( self.simple_dict.A, self.simple_dict.a )
        self.assertEqual( self.simple_dict.B, self.simple_dict.b )
        self.assertEqual( self.simple_dict.C, self.simple_dict.c )

    def test_can_retrieve_by_attr_and_key( self ):
        self.assertEqual( self.simple_dict[ 'A' ], self.simple_dict[ 'a' ] )
        self.assertEqual( self.simple_dict[ 'B' ], self.simple_dict[ 'b' ] )
        self.assertEqual( self.simple_dict[ 'C' ], self.simple_dict[ 'c' ] )

    def test_set_an_attribute_in_upper_case_can_should_be_retrive_in_lower(
            self ):

        new_value = 40
        self.simple_dict.D = new_value
        self.assertEqual( self.simple_dict.d, new_value )
        self.assertEqual( self.simple_dict[ 'd' ], new_value )

    def test_set_a_key_in_upper_case_should_can_be_retrieve_in_lower_case(
            self ):

        new_value = 40
        self.simple_dict[ 'D' ] = new_value
        self.assertEqual( self.simple_dict[ 'd' ], new_value )
        self.assertEqual( self.simple_dict.d, new_value )


class Test_chibi_atlas_ignore_case( TestCase, Test_ignore_case ):
    def setUp( self ):
        self.simple_dict = Chibi_atlas_ignore_case( A=10, B=20, C=30 )


class Test_chibi_atlas_first_parameters_is_a_dict_work(
        TestCase, Test_ignore_case ):
    def setUp( self ):
        self.simple_dict = Chibi_atlas_ignore_case( dict( A=10, B=20, C=30 ) )
