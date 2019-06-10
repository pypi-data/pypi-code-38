from unittest import TestCase

from chibi.file.snippets import inflate_dir, join
from chibi.file.snippets import Chibi_path


class Test_join( TestCase ):

    def setUp( self ):
        self.root = '/'
        self.home = inflate_dir( '~' )

    def test_double_root_is_only_root( self ):
        self.assertEqual( join( self.root, self.root ), join( self.root ) )

    def test_home_and_current_should_end_combined( self ):
        result = join( self.home, 'qwert' )
        self.assertTrue( result.startswith( self.home ) )
        self.assertTrue( result.endswith( 'qwert' ) )

    def test_join_a_chibi_path_and_a_string_should_work( self ):
        a = Chibi_path( '/mnt/hard_drive' )
        b = '12344389.jpg'
        result = join( a, b )
        self.assertEqual( result, '/mnt/hard_drive/12344389.jpg' )
