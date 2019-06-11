
import pytest
from selenium.webdriver.ie.options import Options as IEOptions

from promium.support.settings import SettingsIE


@pytest.mark.unit
def test_driver_capabilities():
    capabilities = SettingsIE.driver_capabilities
    assert capabilities
    assert isinstance(capabilities, dict)
    assert capabilities.get('browserName') == 'internet explorer'


@pytest.mark.unit
def test_binary_path():
    assert SettingsIE.binary_path
    assert 'iedriver' in SettingsIE.binary_path


@pytest.mark.unit
def test_default_options():
    assert len(SettingsIE.default_options) >= 0
    for opt in SettingsIE.default_options:
        assert isinstance(opt, str)


@pytest.mark.unit
def test_driver_options():
    assert isinstance(SettingsIE.driver_options(), IEOptions)


@pytest.mark.unit
def test_get_options_with_default_values():
    SettingsIE.user_options = []
    SettingsIE.default_options = ['-x', '--xxx', '--param -v']
    opt = SettingsIE.get_options()
    assert isinstance(opt, IEOptions)
    assert SettingsIE.default_options == opt.arguments


@pytest.mark.unit
def test_get_options_with_user_values():
    SettingsIE.user_options = ['-x', '--xxx', '--param -v']
    SettingsIE.default_options = []
    opt = SettingsIE.get_options()
    assert isinstance(opt, IEOptions)
    assert SettingsIE.user_options == opt.arguments

