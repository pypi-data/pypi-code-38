import logging
import os
import sys
from glob import glob
from io import StringIO
from unittest.mock import patch

import pytest

from ocdsextensionregistry.cli.__main__ import main

args = ['ocdsextensionregistry', 'download']


def test_command(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3'])
        main()

    assert actual.getvalue() == ''

    tree = list(os.walk(tmpdir))

    assert len(tree) == 4
    # extensions
    assert tree[0][1] == ['location']
    assert tree[0][2] == []
    # versions
    assert tree[1][1] == ['v1.1.3']
    assert tree[1][2] == []
    # files
    assert tree[2][1] == ['codelists']
    assert sorted(tree[2][2]) == ['LICENSE', 'README.md', 'extension.json', 'release-schema.json']
    # codelists
    assert tree[3][1] == []
    assert sorted(tree[3][2]) == ['geometryType.csv', 'locationGazetteers.csv']


def test_command_versions(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location'])
        main()

    assert actual.getvalue() == ''

    tree = list(os.walk(tmpdir))

    assert len(tree[1][1]) > 1


# Take the strictest of restrictions.
def test_command_versions_collision(monkeypatch, tmpdir):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location==v1.1.3', 'location'])
        main()

    assert actual.getvalue() == ''

    tree = list(os.walk(tmpdir))

    assert len(tree[1][1]) == 1


def test_command_versions_invalid(monkeypatch, tmpdir, caplog):
    caplog.set_level(logging.INFO)  # silence connectionpool.py DEBUG messages

    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', args + [str(tmpdir), 'location=v1.1.3'])
            main()

    assert actual.getvalue() == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "Couldn't parse 'location=v1.1.3'. Use '==' not '='."
    assert excinfo.value.code == 1


# Require the user to decide what to overwrite.
def test_command_repeated(monkeypatch, tmpdir, caplog):
    caplog.set_level(logging.INFO)  # silence connectionpool.py DEBUG messages
    argv = args + [str(tmpdir), 'location==v1.1.3']

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', argv)
            main()

    assert actual.getvalue() == ''

    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message.endswith('Set the --overwrite option.')
    assert excinfo.value.code == 1


def test_command_repeated_overwrite_any(monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.3']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove a file, to test whether its download is repeated.
    os.unlink(glob(pattern)[0])

    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'any'])
        main()

    assert actual.getvalue() == ''

    assert len(glob(pattern)) == 1


def test_command_repeated_overwrite_none(monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.3']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove a file, to test whether its download is repeated.
    os.unlink(glob(pattern)[0])

    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'none'])
        main()

    assert actual.getvalue() == ''

    assert len(glob(pattern)) == 0


def test_command_repeated_overwrite_live(monkeypatch, tmpdir):
    argv = args + [str(tmpdir), 'location==v1.1.3', 'location==master']
    pattern = str(tmpdir / '*' / '*' / 'extension.json')

    monkeypatch.setattr(sys, 'argv', argv)
    main()

    # Remove files, to test which downloads are repeated.
    for filename in glob(pattern):
        os.unlink(filename)

    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', argv + ['--overwrite', 'live'])
        main()

    assert actual.getvalue() == ''

    filenames = glob(pattern)

    assert len(filenames) == 1
    assert filenames[0].endswith('/location/master/extension.json')


def test_command_help(monkeypatch, caplog):
    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdsextensionregistry', '--help'])
            main()

    assert actual.getvalue().startswith('usage: ocdsextensionregistry [-h]')

    assert len(caplog.records) == 0
    assert excinfo.value.code == 0
