import os
import tempfile
from syncloudlib.integration.hosts import add_host_alias


def test_add_host_alias():

    fd, path = tempfile.mkstemp()
    try:
        add_host_alias('app', 'localhost', 'tld', path)
        with os.fdopen(fd, 'r') as tmp:
            content = tmp.readlines()
            assert 'localhost.tld' in content[0]
            assert 'app.localhost.tld' in content[1]
    finally:
        os.remove(path)
    