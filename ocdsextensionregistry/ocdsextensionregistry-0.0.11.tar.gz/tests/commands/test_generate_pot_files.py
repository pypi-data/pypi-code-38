import os
import sys
from io import StringIO
from unittest.mock import patch

from ocdsextensionregistry.cli.__main__ import main

args = ['ocdsextensionregistry', 'generate-pot-files']


def test_command(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3'])
        main()

    assert actual.getvalue() == ''

    tree = list(os.walk(tmpdir))

    assert len(tree) == 3
    # extensions
    assert tree[0][1] == ['location']
    assert tree[0][2] == []
    # versions
    assert tree[1][1] == ['v1.1.3']
    assert tree[1][2] == []
    # files
    assert tree[2][1] == []
    assert sorted(tree[2][2]) == ['codelists.pot', 'docs.pot', 'schema.pot']
