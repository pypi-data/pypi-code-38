from unittest import TestCase
from chibi.command.echo import echo


class Test_echo( TestCase ):
    def test_capture_the_output( self ):
        out, error, return_code = echo( 'Hello! my world!!', True )
        self.assertEqual( out, 'Hello! my world!!\n' )
        self.assertFalse( error )
        self.assertEqual( return_code, 0 )
