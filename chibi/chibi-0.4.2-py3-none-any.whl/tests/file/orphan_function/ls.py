from tests.snippet.files import Test_with_files
from chibi.file.snippets import ls


class Test_ls( Test_with_files ):
    def test_should_list_all_the_files_and_dirs_from_root( self ):
        result = list( ls( self.root_dir ) )
        self.assertTrue(
            len( result ) == ( self.amount_of_dirs + self.amount_of_files ) )

    def test_should_return_a_empty_list( self ):
        result = list( ls( self.empty_folder ) )
        self.assertFalse( result )

class Test_ls_recursive( Test_with_files ):
    def test_should_all_the_folders_and_internal_stuff( self ):
        result = set( ls( self.root_dir, recursive=True ) )

        root = set( ls( self.root_dir ) )
        self.assertFalse( root.difference( result ) )
        for r in root:
            rr = set( ls( r ) )
            self.assertFalse( rr.difference( result ) )


    def test_should_return_a_empty_list( self ):
        result = list( ls( self.empty_folder, recursive=True ) )
        self.assertFalse( result )
