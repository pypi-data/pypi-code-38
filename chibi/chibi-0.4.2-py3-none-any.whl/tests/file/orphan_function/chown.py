from chibi.file.snippets import chown, stat
from tests.snippet.files import Test_with_files
from unittest.mock import patch

class Test_chown_to_file( Test_with_files ):
    amount_of_files = 3
    amount_of_dirs = 3

    @patch( 'chibi.file.snippets.print' )
    def test_verbose_when_no_change_the_owners( self, print ):
        current_stat = stat( self.files[0] )
        chown( self.files[0] )
        output = print.call_args_list[0][0][0]
        self.assertIn( 'permanece', output )
        self.assertIn(
            '{}:{}'.format(
                current_stat.user.name, current_stat.group.name ),
            output )
