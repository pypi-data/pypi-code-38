from unittest import TestCase
from chibi.command.echo import ponysay


class Test_ponysay( TestCase ):
    def test_capture_the_output( self ):
        out, error, return_code = ponysay( 'Hello! my world!!', True )
        self.assertIn( 'Hello! my world!!', out )
        self.assertFalse( error )
        self.assertEqual( return_code, 0 )
