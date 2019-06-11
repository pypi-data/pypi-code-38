from unittest import TestCase
from chibi.file.snippets import current_dir, cd
from tests.snippet.files import Test_moving_dir


class Test_cd( Test_moving_dir ):

    def test_ch_can_use_the_simbol_of_home( self ):
        cd( '~' )

    def test_ch_can_use_the_simbol_of_parent_dir( self ):
        cd( '..' )

    def test_ch_for_home_should_change_the_current_directory( self ):
        working_dir = current_dir()
        cd( '~' )
        new_dir = current_dir()
        self.assertNotEqual( working_dir, new_dir )

    def test_ch_for_root_should_change_the_current_directory( self ):
        working_dir = current_dir()
        cd( '/' )
        new_dir = current_dir()
        self.assertNotEqual( working_dir, new_dir )

    def test_ch_for_parent_should_change_the_current_directory( self ):
        working_dir = current_dir()
        cd( '..' )
        new_dir = current_dir()
        self.assertTrue( working_dir.startswith( new_dir ) )

    def test_ch_for_current_dir_should_no_change_the_current_directory( self ):
        working_dir = current_dir()
        cd( '.' )
        new_dir = current_dir()
        self.assertTrue( working_dir.startswith( new_dir ) )
