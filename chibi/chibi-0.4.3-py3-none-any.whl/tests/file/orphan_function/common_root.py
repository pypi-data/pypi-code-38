from unittest import TestCase

from chibi.file.snippets import common_root


class Test_common_root( TestCase ):
    def test_should_return_the_common_root( self ):
        result = common_root( '/usr/var/log', '/usr/var/security' )
        self.assertEqual( '/usr/var/', result  )
