import json
import sys
from io import StringIO
from unittest.mock import patch

from ocdsextensionregistry.cli.__main__ import main
from tests import read

args = ['ocdsextensionregistry', 'generate-data-file']


def test_command(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3'])
        main()

    assert actual.getvalue() == read('location-v1.1.3.json')


def test_command_latest_version_master(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3', 'location==master'])
        main()

    assert json.loads(actual.getvalue())['location']['latest_version'] == 'master'


def test_command_latest_version_dated(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3', 'location==v1.1.1'])
        main()

    assert json.loads(actual.getvalue())['location']['latest_version'] == 'v1.1.3'
