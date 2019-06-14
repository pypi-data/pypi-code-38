import time

import pytest
from mock import patch, MagicMock
from selenium.common.exceptions import TimeoutException

from promium.base import Element
from promium.exceptions import PromiumException
from promium.waits import (
    wait,
    wait_until,
    wait_until_not,
    wait_for_status_code
)
from promium.expected_conditions import is_present


FAKE_LOCATOR = ('', '')


@pytest.fixture()
def driver():
    return MagicMock(name='driver', **{
        'refresh.return_value': 'refresh OK',
        'session_id': '666'
    })


@pytest.mark.unit
def test_base_wait(driver):
    from selenium.webdriver.support.ui import WebDriverWait
    w = wait(driver)
    assert isinstance(w, WebDriverWait)
    assert hasattr(w, 'until')
    assert hasattr(w, 'until_not')


@pytest.mark.unit
@patch.object(Element, '_find_elements', return_value=True)
@pytest.mark.parametrize('seconds, msg', [
    (.01, None),
    (0, ''),
    (.2, 'test error message')
])
def test_wait_until(mock_element, seconds, msg, driver):
    element = Element(*FAKE_LOCATOR)
    start_time = time.time()
    wait_until(driver, is_present(element), seconds, msg)
    end_time = int(time.time() - start_time)
    mock_element.assert_called_once()
    assert end_time == 0, 'Not correct wait time duration'


@pytest.mark.unit
@patch.object(Element, '_find_elements', return_value=False)
@pytest.mark.parametrize('seconds, msg, ex_result', [
    (1, None, 1 * 2),
    (0, '', 1),
    (20, 'test error message', 20 * 2)
])
def test_wait_until_negative(mock_element, seconds, msg, ex_result, driver):
    element = Element(*FAKE_LOCATOR)
    start_time = time.time()
    with pytest.raises(TimeoutException, message='Element is found'):
        wait_until(driver, is_present(element), seconds, msg)
    end_time = int(time.time() - start_time)
    mock_element.assert_called()
    assert mock_element.call_count == ex_result
    assert end_time == seconds, 'Not correct wait time duration'


@pytest.mark.unit
@pytest.mark.parametrize('var, ex, seconds', [
    ([True], 1, 0),
    ([False, True], 2, 0),
    ([False, False, True], 3, 1),
    ([False] * 19 + [True], 20, 9),
])
def test_wait_until_count(var, ex, seconds, driver):
    with patch.object(Element, '_find_elements', side_effect=var) as el:
        element = Element(*FAKE_LOCATOR)
        start_time = time.time()
        wait_until(driver, is_present(element))
        end_time = int(time.time() - start_time)
        el.assert_called()
        assert el.call_count == ex
        assert end_time == seconds, 'Not correct wait time duration'


@pytest.mark.unit
@pytest.mark.parametrize('var, ex, seconds', [
    ([False], 1, 0),
    ([True, False], 2, 0),
    ([True, True, False], 3, 1),
    ([True] * 19 + [False], 20, 9),
])
def test_wait_until_not_positive(var, ex, seconds, driver):
    with patch.object(Element, '_find_elements', side_effect=var) as el:
        element = Element(*FAKE_LOCATOR)
        start_time = time.time()
        wait_until_not(driver, is_present(element))
        end_time = int(time.time() - start_time)
        el.assert_called()
        assert el.call_count == ex
        assert end_time == seconds, 'Not correct wait time duration'


@pytest.mark.unit
@patch.object(Element, '_find_elements', return_value=True)
@pytest.mark.parametrize('ex, seconds', [(1, 0), (2, 1), (10, 5)])
def test_wait_until_not_negative(mock_element, ex, seconds, driver):
    element = Element(*FAKE_LOCATOR)
    start_time = time.time()
    with pytest.raises(PromiumException, message='Element is found'):
        wait_until_not(driver, is_present(element), seconds)
    end_time = int(time.time() - start_time)
    mock_element.assert_called()
    assert mock_element.call_count == ex
    assert end_time == seconds, 'Not correct wait time duration'


@pytest.mark.unit
@pytest.mark.parametrize('var, ex, ex_sec', [
    ([True], 1, 0),
    ([False, True], 2, 0),
    ([False, False, True], 3, 1),
    ([False, False] * 9 + [True], 19, 9),
])
def test_wait_until_with_reload(var, ex, ex_sec, driver):
    with patch.object(Element, '_find_elements', side_effect=var) as el:
        element = Element(*FAKE_LOCATOR)
        start_time = time.time()
        wait_until(
            driver=driver,
            expression=is_present(element, with_refresh=True),
            seconds=10
        )
        end_time = int(time.time() - start_time)
        el.assert_called()
        assert el.call_count == ex
        assert end_time == ex_sec, 'Not correct wait time duration'
        driver.refresh.assert_called()
        assert driver.refresh.call_count == ex


@pytest.mark.unit
@patch.object(Element, '_find_elements', return_value=False)
@pytest.mark.parametrize('ex, sec', [(1, 0), (2, 1), (20, 10)])
def test_wait_until_with_reload_negative(mock_element, ex, sec, driver):
    element = Element(*FAKE_LOCATOR)
    start_time = time.time()
    with pytest.raises(TimeoutException):
        wait_until(
            driver=driver,
            expression=is_present(element, with_refresh=True),
            seconds=sec
        )
    end_time = int(time.time() - start_time)
    mock_element.assert_called()
    assert end_time == sec, 'Not correct wait time duration'
    driver.refresh.assert_called()
    assert driver.refresh.call_count == ex


@pytest.mark.skip('Not implemented')
@pytest.mark.unit
def test_wait_for_alert():
    pass


@pytest.mark.skip('Not implemented')
@pytest.mark.unit
def test_wait_for_alert_negative():
    pass


@pytest.mark.unit
@pytest.mark.parametrize('tries', [1, 2, 10, 15])
def test_wait_for_status_code(tries):
    start_time = time.time()
    wait_for_status_code('http://google.com/page?id=666', 404, tries)
    end_time = int(time.time() - start_time)
    assert end_time == 0


@pytest.mark.unit
@pytest.mark.parametrize('tries', [1, 2, 5])
def test_wait_for_status_code_negative(tries):
    start_time = time.time()
    with pytest.raises(PromiumException):
        wait_for_status_code('http://google.com/page?id=666', 200, tries)
    end_time = int(time.time() - start_time)
    assert end_time == tries


@pytest.mark.skip('Not implemented')
@pytest.mark.unit
def test_wait_until_new_window_is_opened():
    pass


@pytest.mark.skip('Not implemented')
@pytest.mark.unit
def test_wait_until_new_window_is_opened_negative():
    pass
