
import pytest
from selenium.webdriver.edge.options import Options as EdgeOptions

from promium.support.settings import SettingsEDGE


@pytest.mark.unit
def test_driver_capabilities():
    capabilities = SettingsEDGE.driver_capabilities
    assert capabilities
    assert isinstance(capabilities, dict)
    assert capabilities.get('browserName') == 'MicrosoftEdge'


@pytest.mark.unit
def test_binary_path():
    assert SettingsEDGE.binary_path
    assert 'edgedriver' in SettingsEDGE.binary_path


@pytest.mark.unit
def test_default_options():
    assert len(SettingsEDGE.default_options) >= 0
    for opt in SettingsEDGE.default_options:
        assert isinstance(opt, str)


@pytest.mark.unit
def test_driver_options():
    assert isinstance(SettingsEDGE.driver_options(), EdgeOptions)


@pytest.mark.unit
def test_get_options():
    assert isinstance(SettingsEDGE.get_options(), EdgeOptions)
