import os
from tempfile import mkdtemp

import pytest


def test_bare_apps(cli):
    c = cli('apps')
    assert 'Usage' in c.out


def test_apps_create(cli):
    # Make a temporary directory to
    loc = mkdtemp()
    os.makedirs(loc, exist_ok=True)

    old_location = os.curdir
    os.chdir(loc)

    # Create the application.
    c = cli('apps', 'create')

    # Destroy the application.
    cli('apps', 'destroy')

    # Switch back to previous directory.
    os.chdir(old_location)

    assert 'Creating' in c.out
    assert c.return_code == 0
