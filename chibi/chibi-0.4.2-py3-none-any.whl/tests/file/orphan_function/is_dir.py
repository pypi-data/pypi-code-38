from unittest import TestCase
from chibi.file.snippets import is_dir
from tests.snippet.files import Test_with_files


class Test_is_dir( Test_with_files ):
    amount_of_files = 3
    amount_of_dirs = 3

    def test_root_should_be_a_true( self ):
        self.assertTrue( is_dir( self.root_dir ) )

    def test_all_dirs_list_should_be_true( self ):
        for dir in self.dirs:
            self.assertTrue( is_dir( dir ) )

    def test_all_files_liist_should_be_false( self ):
        for file in self.files:
            self.assertFalse( is_dir( file ) )
