
import os

import pytest
from selenium.webdriver.chrome.options import Options as ChromeOptions

from promium.support.settings import SettingsChrome


@pytest.mark.unit
def test_driver_capabilities():
    assert SettingsChrome.driver_capabilities
    assert isinstance(SettingsChrome.driver_capabilities, dict)
    assert SettingsChrome.driver_capabilities.get('browserName') == 'chrome'


@pytest.mark.unit
def test_binary_path():
    assert SettingsChrome.binary_path
    assert 'chromedriver' in SettingsChrome.binary_path


@pytest.mark.unit
def test_default_options():
    assert len(SettingsChrome.default_options) > 0
    for opt in SettingsChrome.default_options:
        assert isinstance(opt, str)


@pytest.mark.unit
def test_default_exp_options():
    assert len(SettingsChrome.default_exp_options) > 0
    assert 'prefs' in SettingsChrome.default_exp_options.keys()


@pytest.mark.unit
def test_driver_options():
    assert isinstance(SettingsChrome.driver_options(), ChromeOptions)


@pytest.mark.unit
def test_get_options_with_default_values():
    os.environ['HEADLESS'] = ''
    SettingsChrome.user_exp_options = {}
    SettingsChrome.user_options = []
    opt = SettingsChrome.get_options()
    assert isinstance(opt, ChromeOptions)
    assert SettingsChrome.default_exp_options == opt.experimental_options
    assert SettingsChrome.default_options == opt.arguments


@pytest.mark.unit
def test_get_options_with_user_values():
    os.environ['HEADLESS'] = ''
    SettingsChrome.user_exp_options = {'key1': 1}
    SettingsChrome.user_options = ['param1', 'param2', '--param3', '-p4']
    opt = SettingsChrome.get_options()
    assert isinstance(opt, ChromeOptions)
    assert SettingsChrome.user_exp_options == opt.experimental_options
    assert SettingsChrome.user_options == opt.arguments


@pytest.mark.unit
def test_get_options_without_headless():
    os.environ['HEADLESS'] = ''
    SettingsChrome.user_exp_options = {}
    SettingsChrome.user_options = []
    opt = SettingsChrome.get_options()
    assert isinstance(opt, ChromeOptions)
    assert '--headless' not in opt.arguments


@pytest.mark.unit
def test_get_options_with_headless():
    os.environ['HEADLESS'] = 'Enabled'
    SettingsChrome.user_exp_options = {}
    SettingsChrome.user_options = []
    opt = SettingsChrome.get_options()
    assert isinstance(opt, ChromeOptions)
    assert '--headless' in opt.arguments
    assert '--disable-gpu' in opt.arguments
