from chibi.command import yum
from unittest.mock import patch, ANY
from unittest import TestCase


class Test_localinstall( TestCase ):
    @patch( 'chibi.command.Popen' )
    def test_local_install_use_the_argument_yes( self, popen_mock ):
        popen_mock.side_effect = Exception
        try:
            yum.local_install( 'ruby' )
        except Exception:
            pass
        popen_mock.assert_called_with(
            ( 'yum', 'localinstall', '-y', ANY, ), stderr=ANY, stdout=ANY )
