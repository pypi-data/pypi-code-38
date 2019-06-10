import chibi
import unittest


class Test_b64( unittest.TestCase ):
    def setUp( self ):
        self.encode = 'YXNkZg=='
        self.decode = 'asdf'

    def test_encode( self ):
        self.assertEqual( chibi.b64.encode( self.decode ), self.encode )

    def test_decode( self ):
        self.assertEqual( chibi.b64.decode( self.encode ), self.decode )
