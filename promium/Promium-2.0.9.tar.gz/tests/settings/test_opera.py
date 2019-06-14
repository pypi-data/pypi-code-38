
import pytest

from promium.support.settings import SettingsOpera


@pytest.mark.unit
def test_driver_capabilities():
    assert SettingsOpera.driver_capabilities
    assert isinstance(SettingsOpera.driver_capabilities, dict)
    assert SettingsOpera.driver_capabilities.get('browserName') == 'opera'


@pytest.mark.unit
def test_binary_path():
    assert SettingsOpera.binary_path
    assert 'opera' in SettingsOpera.binary_path
