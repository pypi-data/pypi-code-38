from mock import patch

import pytest

from burlap.tests.base import TestCase

class SystemTests(TestCase):

    def test_unsupported_system(self):

        from burlap.system import UnsupportedFamily

        with pytest.raises(UnsupportedFamily) as excinfo:

            with patch('burlap.system.distrib_id') as mock_distrib_id:
                mock_distrib_id.return_value = 'foo'

                raise UnsupportedFamily(supported=['debian', 'redhat'])

        exception_msg = str(excinfo.value)
        assert exception_msg == "Unsupported family other (foo). Supported families: debian, redhat"
