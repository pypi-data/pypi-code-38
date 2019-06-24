#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `anonapi.settings` module."""
from distutils import dir_util
from pathlib import Path

import pytest

from anonapi.settings import (
    AnonClientSettingsFromFile,
    AnonClientSettingsException,
    AnonClientSettings,
    DefaultAnonClientSettings,
)
from tests import RESOURCE_PATH


@pytest.fixture
def test_settings_folder(tmp_path):
    """A one-time copy of a folder containing some settings files

    Returns
    -------
    str
        path to folder

    """
    template_folder = Path(RESOURCE_PATH) / "test_settings"
    dir_util.copy_tree(str(template_folder), str(tmp_path))
    return tmp_path


@pytest.fixture
def test_settings_file(test_settings_folder):
    """Copy of a correctly formatted settings file """
    return test_settings_folder / "settings.yml"


def test_settings_load(test_settings_file):
    settings = AnonClientSettingsFromFile(test_settings_file)

    assert settings.user_name == "kees"
    assert settings.user_token == "token"
    assert settings.active_server.name == "sandbox"
    assert len(settings.servers) == 2
    assert str(settings) == f"Settings at {str(test_settings_file)}"


def test_settings_save(test_settings_file):
    """Load settings, change, save and see whether they have been saved
    """
    settings = AnonClientSettingsFromFile(test_settings_file)

    assert settings.user_name == "kees"

    settings.user_name = "other_username"
    settings.save()

    # load new settings from the same file to rule out any data being persisted in object
    new_settings = AnonClientSettingsFromFile(filename=test_settings_file)
    assert new_settings.user_name == "other_username"


def test_settings_save_with_none_active(test_settings_file):
    """ fixing a bug found live: saving when active server = none
    """
    settings = AnonClientSettingsFromFile(test_settings_file)

    # It is possible that there is no active server. You should still be able to save
    settings.active_server = None
    settings.save()

    # And also load
    new_settings = AnonClientSettingsFromFile(filename=test_settings_file)
    assert new_settings.active_server is None


def test_settings_load_error(test_settings_folder):
    """ Poor mans YAML validation should at least raise some informative exception when a key is missing from
    settings
    """
    settings_file_wrong = test_settings_folder / "settings_wrong.yml"
    with pytest.raises(AnonClientSettingsException):
        AnonClientSettingsFromFile(settings_file_wrong)


def test_settings_load_error2(test_settings_folder):
    """ Some more easy errors to make when manually editing settings file
    """
    settings_file_wrong = test_settings_folder / "settings_wrong_2.yml"
    with pytest.raises(AnonClientSettingsException):
        AnonClientSettingsFromFile(settings_file_wrong)


def test_anon_client_settings_init_with_no_servers():
    # this should not crash
    _ = AnonClientSettings(servers=[], user_name="test", user_token="token")
    _ = DefaultAnonClientSettings()
