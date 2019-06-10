
import os

import pytest
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from promium.device_config import Device
from promium.support.settings import SettingsFirefox


@pytest.mark.unit
def test_driver_capabilities():
    assert SettingsFirefox.driver_capabilities
    assert isinstance(SettingsFirefox.driver_capabilities, dict)
    assert SettingsFirefox.driver_capabilities.get('browserName') == 'firefox'


@pytest.mark.unit
def test_binary_path():
    assert SettingsFirefox.binary_path
    assert 'gekodriver' in SettingsFirefox.binary_path


@pytest.mark.unit
def test_default_options():
    assert len(SettingsFirefox.default_options) > 0
    for opt in SettingsFirefox.default_options:
        assert isinstance(opt, str)


@pytest.mark.unit
def test_default_preferences():
    assert len(SettingsFirefox.default_preferences) > 0
    for opt in SettingsFirefox.default_options:
        assert isinstance(opt, str)


@pytest.mark.unit
def test_driver_options():
    assert isinstance(SettingsFirefox.driver_options(), FirefoxOptions)


@pytest.mark.unit
def test_set_windows_size():
    SettingsFirefox.device = Device(
         width=123, height=321, user_agent='xxx', device_name=''
    )
    SettingsFirefox.set_windows_size()
    ex_options = [
        '-width {}'.format(SettingsFirefox.device.width),
        '-height {}'.format(SettingsFirefox.device.height)
    ]
    for opt in ex_options:
        assert opt in SettingsFirefox.default_options


@pytest.mark.unit
def test_set_windows_size_with_device():
    device = Device(
        width=123, height=321, user_agent='user xxx', device_name=''
    )
    SettingsFirefox.set_windows_size(device)
    ex_options = [
        '-width {}'.format(SettingsFirefox.device.width),
        '-height {}'.format(SettingsFirefox.device.height)
    ]
    for opt in ex_options:
        assert opt in SettingsFirefox.default_options


@pytest.mark.unit
def test_get_options_with_default_values():
    os.environ['HEADLESS'] = ''
    SettingsFirefox.user_exp_options = {}
    SettingsFirefox.user_options = []
    opt = SettingsFirefox.get_options()
    assert isinstance(opt, FirefoxOptions)
    assert SettingsFirefox.default_options == opt.arguments


@pytest.mark.unit
def test_get_options_with_user_values():
    os.environ['HEADLESS'] = ''
    SettingsFirefox.user_exp_options = {'key1': 1}
    SettingsFirefox.user_options = ['param1', 'param2', '--param3', '-p4']
    opt = SettingsFirefox.get_options()
    assert isinstance(opt, FirefoxOptions)
    assert SettingsFirefox.user_options == opt.arguments


@pytest.mark.unit
def test_get_options_with_headless():
    os.environ['HEADLESS'] = 'false'
    SettingsFirefox.user_exp_options = {}
    SettingsFirefox.user_options = []
    opt = SettingsFirefox.get_options()
    assert isinstance(opt, FirefoxOptions)
    assert '-headless' not in opt.arguments


@pytest.mark.unit
def test_get_options_with_headless():
    os.environ['HEADLESS'] = 'Enabled'
    SettingsFirefox.user_exp_options = {}
    SettingsFirefox.user_options = []
    opt = SettingsFirefox.get_options()
    assert isinstance(opt, FirefoxOptions)
    assert '-headless' in opt.arguments


@pytest.mark.unit
def test_get_preferences():
    profile = SettingsFirefox.get_preferences()
    for pr in SettingsFirefox.default_preferences.keys():
        assert pr in profile.default_preferences


@pytest.mark.unit
def test_get_preferences_with_user_values():
    SettingsFirefox.user_preferences = {'key1': 1}
    profile = SettingsFirefox.get_preferences()
    for user_pr in SettingsFirefox.user_preferences.keys():
        assert user_pr in profile.default_preferences


@pytest.mark.unit
@pytest.mark.parametrize('user_agent', ['', None])
def test_get_preferences_with_user_agent_preferences(user_agent):
    SettingsFirefox.device = Device(
        width=123, height=321, user_agent=user_agent, device_name=''
    )
    profile = SettingsFirefox.get_preferences()
    assert not profile.default_preferences.get('general.useragent.override')


@pytest.mark.unit
def test_get_preferences_with_user_agent():
    SettingsFirefox.device = Device(
        width=123, height=321, user_agent='user agent xxx', device_name=''
    )
    profile = SettingsFirefox.get_preferences()
    user_agent = profile.default_preferences.get('general.useragent.override')
    assert user_agent == 'user agent xxx'
