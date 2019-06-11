from tests.snippet.files import Test_with_files
from chibi.file import Chibi_file


class Test_chibi_file_check_sum_md5( Test_with_files ):
    def setUp( self ):
        super().setUp()
        self.chibi_file = Chibi_file( self.files[0] )

    def test_should_do_check_sum_empty_file( self ):
        self.assertTrue(
            self.chibi_file.check_sum_md5( '1B2M2Y8AsgTpgAmY7PhCfg==' ) )
