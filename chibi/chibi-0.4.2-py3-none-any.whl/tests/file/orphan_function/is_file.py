from chibi.file.snippets import is_file
from tests.snippet.files import Test_with_files


class Test_is_file( Test_with_files ):
    amount_of_files = 3
    amount_of_dirs = 3

    def test_root_should_be_a_false( self ):
        self.assertFalse( is_file( self.root_dir ) )

    def test_all_dirs_list_should_be_false( self ):
        for dir in self.dirs:
            self.assertFalse( is_file( dir ) )

    def test_all_files_liist_should_be_true( self ):
        for file in self.files:
            self.assertTrue( is_file( file ) )
