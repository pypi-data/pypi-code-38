from tests.snippet.files import Test_with_files
from chibi.file.snippets import exists, join


class Test_exists( Test_with_files ):
    def test_should_be_true_with_a_file_exists( self ):
        for file in self.files:
            self.assertTrue( exists( file ) )

    def test_should_be_true_with_dirs( self ):
        self.assertTrue( exists( self.root_dir ) )
        for dir in self.dirs:
            self.assertTrue( exists( dir ) )

    def test_should_be_false_when_dont_exists_the_file( self ):
        self.assertFalse( exists( join( self.empty_folder, 'some_file' ) ) )
