import os
import pytest
from cocktail_apikit import SettingManager, DefaultSettings


@pytest.fixture(scope='function')
def simple_settings():
    class Settings(DefaultSettings):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


@pytest.fixture(scope='function')
def file_settings():
    class Settings(DefaultSettings):
        _config_files = ['config/db.ini']
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


@pytest.fixture(scope='function')
def manager_settings():
    class SecretManager(SettingManager):
        DEFAULT = {'DATABASE_URI': 'manager_uri'}
        TEST = {'DATABASE_URI': 'manager_test_uri'}

    class Settings(DefaultSettings):
        _setting_managers = [SecretManager]
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


@pytest.fixture(scope='function')
def mixed_settings():
    class SecretManager(SettingManager):
        DEFAULT = {'DATABASE_URI': 'manager_uri'}
        TEST = {'DATABASE_URI': 'manager_test_uri'}

    class Settings(DefaultSettings):
        _config_files = ['config/db.ini']
        _setting_managers = [SecretManager]
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


@pytest.fixture(scope='function')
def mixed_settings_with_none_value():
    class SecretManager(SettingManager):
        ALLOW_NONE_VALUE = True
        DEFAULT = {'DATABASE_URI': 'manager_uri'}
        TEST = {'DATABASE_URI': None}

    class Settings(DefaultSettings):
        _config_files = ['config/db.ini']
        _setting_managers = [SecretManager]
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


@pytest.fixture(scope='function')
def mixed_settings_with_customized_value():
    class SecretManager(SettingManager):

        DEFAULT = {'DATABASE_URI': 'manager_uri'}
        TEST = {'DATABASE_URI': 'test_uri'}

        def test_settings(self):
            config = super().test_settings()
            config.update({'DATABASE_URI': 'customized_uri'})
            return config

    class Settings(DefaultSettings):
        _config_files = ['config/db.ini']
        _setting_managers = [SecretManager]
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DATABASE_URI = 'class_uri'

    return Settings


def test_mixed_settings_with_customized_value(
        mixed_settings_with_customized_value):
    assert mixed_settings_with_customized_value.DATABASE_URI == 'customized_uri'


def test_simple_settings(simple_settings):
    assert simple_settings.DATABASE_URI == 'class_uri'


def test_file_settings(file_settings):
    assert file_settings.DATABASE_URI == 'file_uri'


def test_manager_settings(manager_settings):
    assert manager_settings.DATABASE_URI == 'manager_test_uri'


def test_mixed_settings(mixed_settings):
    assert mixed_settings.DATABASE_URI == 'manager_test_uri'


def test_mixed_settings_with_none_value(mixed_settings_with_none_value):
    assert mixed_settings_with_none_value.DATABASE_URI is None
