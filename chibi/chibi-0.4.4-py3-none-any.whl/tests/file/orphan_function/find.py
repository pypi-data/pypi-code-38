from tests.snippet.files import Test_with_files
from chibi.file.snippets import (
    ls, find, base_name, is_a_file, is_a_folder, find_only_files,
    find_only_folders,
)


class Test_find( Test_with_files ):
    defined_folders = [ 'a', 'b' ]
    defined_files = [ 'w', 'q', 'a/e', 'b/r' ]

    def test_without_search_should_be_the_same_to_ls( self ):
        result = set( find( self.root_dir ) )
        ls_result = set( ls( self.root_dir, recursive=True ) )
        self.assertSetEqual( result, ls_result )

    def test_should_find_the_file( self ):
        result = set( find( self.root_dir, search_term='w' ) )
        result = [ a for a in result if base_name( a ) == 'w' ]
        self.assertEqual( len( result ), 1 )

    def test_should_find_files_in_folder( self ):
        result = set( find( self.root_dir, search_term='e' ) )
        result = [ a for a in result if base_name( a ) == 'e' ]
        self.assertEqual( len( result ), 1 )


class Test_find_only_files( Test_with_files ):
    defined_folders = [ 'a', 'b' ]
    defined_files = [ 'w', 'q', 'a/e', 'b/r' ]

    def test_without_search_should_be_the_same_to_ls( self ):
        result = set( find_only_files( self.root_dir ) )
        self.assertTrue( all( is_a_file( r ) for r in result ) )


class Test_find_only_folders( Test_with_files ):
    defined_folders = [ 'a', 'b' ]
    defined_files = [ 'w', 'q', 'a/e', 'b/r' ]

    def test_without_search_should_be_the_same_to_ls( self ):
        result = set( find_only_folders( self.root_dir ) )
        self.assertTrue( all( is_a_folder( r ) for r in result ) )
