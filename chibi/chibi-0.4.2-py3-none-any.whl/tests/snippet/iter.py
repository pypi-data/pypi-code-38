from unittest import TestCase

from chibi.snippet.iter import cut_until, chunk_each


class Test_cut_until( TestCase ):
    def setUp( self ):
        self.iterable = 'aaaaabaaabaabab'

    def test_should_return_5a( self ):
        result = cut_until( iter( self.iterable ), lambda x: x != 'a' )
        self.assertEqual( 'aaaaa', "".join( result ) )


class Test_chunk_each( TestCase ):
    def setUp( self ):
        self.iterable = 'baaaabccccbddddbqqqq'

    def test_should_return_5a( self ):
        result = chunk_each( self.iterable, lambda x: x == 'b' )
        for r in result:
            s = "".join( r )
            self.assertEqual( len( s ), 5 )
