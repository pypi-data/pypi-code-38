from chibi.parser import to_bool
from unittest import TestCase


class Test_to_bool( TestCase ):
    def setUp( self ):
        self.list_of_conbinations_to_bool = [
            ( 'false', False ), ( 'true', True ), ( '0', False ),
            ( '1', True ), ( object(), True ), ( 0, False ), ( 1, True ),
            ( 'Y', True ), ( 'y', True ), ( 'N', False ), ( 'n', False ),
        ]

    def test_the_list_of_combinations_should_return_all_the_expects( self ):
        for value, expected in self.list_of_conbinations_to_bool:
            result = to_bool( value )
            self.assertEqual(
                result, expected,
                "se esperaba {} con el valor de {} pero se obtubo {}"
                    .format( expected, value, result ) )
