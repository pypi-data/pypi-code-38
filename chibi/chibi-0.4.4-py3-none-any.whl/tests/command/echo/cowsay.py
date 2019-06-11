from unittest import TestCase
from chibi.command.echo import cowsay


class Test_cowsay( TestCase ):
    def test_capture_the_output( self ):
        out, error, return_code = cowsay( 'Hello! my world!!', True )
        self.assertIn( 'Hello! my world!!', out )
        self.assertFalse( error )
        self.assertEqual( return_code, 0 )
