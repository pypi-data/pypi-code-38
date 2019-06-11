
import os

import pytest

from promium.device_config import CHROME_DESKTOP_1024_768, Device
from promium.support.settings import (
    BASE_CAPABILITIES,
    get_download_path,
    SettingsDrivers,
    SettingsChrome,
    SettingsOpera,
    SettingsEDGE,
    SettingsIE,
    SettingsFirefox,
    Base,
)


@pytest.mark.unit
@pytest.mark.parametrize('driver, ex_settings', [
    ('chrome', SettingsChrome),
    ('opera', SettingsOpera),
    ('firefox', SettingsFirefox),
    ('edge', SettingsEDGE),
    ('ie', SettingsIE),
])
def test_get_driver_settings(driver, ex_settings):
    assert isinstance(SettingsDrivers().get(driver), ex_settings)


@pytest.mark.unit
def test_get_driver_settings_negative():
    with pytest.raises(ValueError):
        SettingsDrivers().get('chromium')


@pytest.mark.unit
def test_get_download_path():
    assert get_download_path() == '/tmp'


@pytest.mark.unit
def test_get_download_path_with_env():
    os.environ.setdefault('DOWNLOAD_PATH', '/xxx/123')
    assert get_download_path() == '/xxx/123'


@pytest.mark.unit
def test_driver_capabilities():
    assert isinstance(Base.driver_capabilities, dict)
    assert not Base.driver_capabilities


@pytest.mark.unit
def test_default_capabilities():
    assert isinstance(Base.default_capabilities, dict)
    assert Base.default_capabilities  == BASE_CAPABILITIES


@pytest.mark.unit
def test_user_capabilities():
    assert isinstance(Base.user_capabilities, dict)
    assert not Base.user_capabilities


@pytest.mark.unit
def test_binary_path():
    assert isinstance(Base.binary_path, str)
    assert not Base.binary_path


@pytest.mark.unit
def test_device():
    assert isinstance(Base.device, tuple)
    assert Base.device == CHROME_DESKTOP_1024_768


@pytest.mark.unit
def test_default_options():
    assert isinstance(Base.default_options, list)
    assert not Base.default_options


@pytest.mark.unit
def test_user_options():
    assert isinstance(Base.user_options, list)
    assert not Base.user_options


@pytest.mark.unit
def test_default_experimental_options():
    assert isinstance(Base.default_exp_options, dict)
    assert not Base.default_exp_options


@pytest.mark.unit
def test_user_experimental_options():
    assert isinstance(Base.user_exp_options, dict)
    assert not Base.user_exp_options


@pytest.mark.unit
def test_default_preferences():
    assert isinstance(Base.default_preferences, dict)
    assert not Base.default_preferences


@pytest.mark.unit
def test_user_preferences():
    assert isinstance(Base.user_preferences, dict)
    assert not Base.user_preferences


@pytest.mark.unit
def test_driver_options():
    with pytest.raises(NotImplementedError):
        Base.driver_options()


@pytest.mark.unit
def test_options():
    assert Base.options() == []


@pytest.mark.unit
def test_options_with_default_values():
    Base.default_options = ['x']
    assert Base.options() == ['x']


@pytest.mark.unit
def test_options_with_user_values():
    Base.user_options = ['x']
    assert Base.options() == ['x']


@pytest.mark.unit
def test_options_with_user_and_default_values():
    Base.user_options = ['x1']
    Base.default_options = ['x2']
    assert Base.options() == ['x1']


@pytest.mark.unit
def test_experimental_options():
    assert Base.experimental_options() == {}


@pytest.mark.unit
def test_experimental_options_with_default_values():
    Base.default_exp_options = {'key1': 1}
    assert Base.experimental_options() == {'key1': 1}


@pytest.mark.unit
def test_experimental_options_with_user_values():
    Base.user_exp_options = {'key2': 2}
    assert Base.experimental_options() == {'key2': 2}


@pytest.mark.unit
def test_experimental_options_with_user_and_default_values():
    Base.user_exp_options = {'key2': 2}
    Base.default_exp_options = {'key1': 1}
    assert Base.experimental_options() == {'key2': 2}


@pytest.mark.unit
def test_capabilities():
    assert Base.capabilities() == BASE_CAPABILITIES


@pytest.mark.unit
def test_capabilities_with_default_values():
    Base.default_capabilities = {'key1': 1}
    assert Base.capabilities() == {'key1': 1}


@pytest.mark.unit
def test_capabilities_with_user_values():
    Base.user_capabilities = {'key2': 2}
    assert Base.capabilities() == {'key2': 2}


@pytest.mark.unit
def test_capabilities_with_user_and_default_values():
    Base.user_capabilities = {'key3': 3}
    assert Base.default_capabilities
    assert Base.capabilities() == {'key3': 3}


@pytest.mark.unit
def test_preference():
    assert Base.preference() == {}


@pytest.mark.unit
def test_preference_with_default_values():
    Base.default_preferences = {'key1': 1}
    assert Base.preference() == {'key1': 1}


@pytest.mark.unit
def test_preference_with_user_values():
    Base.user_preferences = {'key2': 2}
    assert Base.preference() == {'key2': 2}


@pytest.mark.unit
def test_preference_with_user_and_default_values():
    Base.user_preferences = {'key1': 1}
    Base.default_preferences = {'key2': 2}
    assert Base.preference() == {'key1': 1}


@pytest.mark.unit
def test_set_device():
    Base.set_device(
        width=666, height=13, user_agent='user agent xxx', device_name=''
    )
    assert Base.device == Device(
        width=666, height=13, user_agent='user agent xxx', device_name=''
    )


@pytest.mark.unit
def test_set_device_without_user_agent():
    Base.set_device(width=123, height=321, user_agent='', device_name='')
    assert Base.device == Device(
        width=123, height=321, user_agent='', device_name=''
    )


@pytest.mark.unit
def test_set_options():
    Base.user_options = []
    Base.set_options('xxx', '123')
    assert Base.user_options == ['xxx', '123']


@pytest.mark.unit
def test_add_option():
    assert 'xxx' not in Base.default_options
    Base.add_option('xxx')
    assert 'xxx' in Base.default_options


@pytest.mark.unit
def test_delete_option():
    Base.default_options = ['xxx']
    Base.delete_option('xxx')
    assert 'xxx' not in Base.default_options


@pytest.mark.unit
def test_set_windows_size():
    Base.device = Device(
        width=123, height=321, user_agent='xxx', device_name=''
    )
    Base.set_windows_size()
    ex_options = [
        '--user-agent={}'.format(Base.device.user_agent),
        '--window-size={},{}'.format(Base.device.width, Base.device.height)
    ]
    for opt in ex_options:
        assert opt in Base.default_options


@pytest.mark.unit
@pytest.mark.parametrize('params', [(123, 321, '', ''), (321, 123, None, '')])
def test_set_windows_size_without_user_agent(params):
    Base.device = Device(*params)
    Base.set_windows_size()
    ex_option = '--window-size={},{}'.format(
        Base.device.width, Base.device.height
    )
    assert ex_option in Base.default_options


@pytest.mark.unit
def test_set_windows_size_with_device():
    device = Device(
        width=123, height=321, user_agent='user xxx', device_name=''
    )
    Base.set_windows_size(device)
    ex_options = [
        '--user-agent={}'.format(device.user_agent),
        '--window-size={},{}'.format(device.width, device.height)
    ]
    for opt in ex_options:
        assert opt in Base.default_options


@pytest.mark.unit
def test_get_options():
    with pytest.raises(NotImplementedError):
        Base.get_options()


@pytest.mark.unit
def test_get_capabilities():
    Base.default_capabilities = BASE_CAPABILITIES
    Base.user_capabilities = {}
    assert Base.get_capabilities() == BASE_CAPABILITIES


@pytest.mark.unit
def test_get_capabilities_with_user_values():
    Base.default_capabilities = BASE_CAPABILITIES
    Base.user_capabilities = {'key1': 1}
    assert Base.get_capabilities() == {'key1': 1}


@pytest.mark.unit
def test_base_set_preferences():
    Base.default_preferences = {}
    Base.user_preferences = {}
    Base.set_preferences(key1=1, key2=2)
    assert Base.user_preferences == {'key1': 1, 'key2': 2}


@pytest.mark.unit
def test_base_update_preferences():
    Base.default_preferences = {}
    Base.user_preferences = {}
    Base.update_preferences(key1=1, key2=2)
    assert Base.default_preferences == {'key1': 1, 'key2': 2}


@pytest.mark.unit
def test_base_delete_preferences():
    Base.default_preferences = {'key1': 1}
    Base.delete_preference('key1')
    assert Base.default_preferences == {}


@pytest.mark.unit
def test_get_preferences():
    assert Base.get_preferences() is None
