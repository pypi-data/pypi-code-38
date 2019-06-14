import logging
import requests
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    WebDriverException,
    TimeoutException
)

from promium.exceptions import PromiumException, PromiumTimeout
from promium.logger import find_console_browser_errors, repr_console_errors


log = logging.getLogger(__name__)

JQUERY_LOAD_TIME = 10
AJAX_LOAD_TIME = 10
ANIMATION_LOAD_TIME = 10


def _check_browser_console(driver):
    """
    for using when exception occurs
    and default check console methods don`t work
    """
    console_errors = find_console_browser_errors(driver)
    if console_errors:
        log.warning(repr_console_errors(console_errors))


def enable_jquery(driver):
    """Enables jquery"""
    driver.execute_script(
        """
        jqueryUrl =
        'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js';
        if (typeof jQuery == 'undefined') {
            var script = document.createElement('script');
            var head = document.getElementsByTagName('head')[0];
            var done = false;
            script.onload = script.onreadystatechange = (function() {
                if (!done && (!this.readyState || this.readyState == 'loaded'
                        || this.readyState == 'complete')) {
                    done = true;
                    script.onload = script.onreadystatechange = null;
                    head.removeChild(script);

                }
            });
            script.src = jqueryUrl;
            head.appendChild(script);
        };
        """
    )


def wait(driver, seconds=10, poll_frequency=.5, ignored_exceptions=None):
    """Waits in seconds"""
    return WebDriverWait(
        driver=driver,
        timeout=seconds,
        poll_frequency=poll_frequency,
        ignored_exceptions=ignored_exceptions or [WebDriverException]
    )


def wait_until(driver, expression, seconds=10, msg=None):
    """Waits until expression execution"""
    try:
        return wait(driver, seconds).until(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise TimeoutException(e.msg, seconds)


def wait_until_not(driver, expression, seconds=10, msg=None):
    """Waits until not expression execution"""
    try:
        return wait(driver, seconds).until_not(expression, msg)
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, seconds)


def wait_until_with_reload(driver, expression, trying=5, seconds=2, msg=''):
    """Waits until expression execution with page refreshing"""
    for t in range(trying):
        try:
            driver.refresh()
            if wait_until(driver, expression, seconds=seconds):
                return
        except PromiumTimeout:
            log.warning(f"Waiting `until` attempt number {t + 1}.")
    msg = f'\n{msg}' if msg else ""
    raise PromiumTimeout(
        f'The values in expression not return true after {trying} tries {msg}',
        seconds=trying * seconds,
    )


def wait_until_not_with_reload(
        driver, expression, trying=5, seconds=2, msg=''
):
    """Waits until not expression execution with page refreshing"""
    for t in range(trying):
        try:
            driver.refresh()
            if not wait_until_not(driver, expression, seconds=seconds):
                return
        except PromiumTimeout:
            log.warning(f"Waiting `until not` attempt number {t + 1}.")
    msg = f'\n{msg}' if msg else ""
    raise PromiumTimeout(
        f'The values in expression not return false after {trying} '
        f'tries {msg}.',
        seconds=trying * seconds,
    )


def wait_for_ajax(driver):
    """Waits for execution ajax"""
    try:
        jquery_script = 'return typeof jQuery != "undefined"'
        enable_jquery(driver)
        wait_until(
            driver=driver,
            expression=lambda d: d.execute_script(jquery_script),
            seconds=JQUERY_LOAD_TIME,
            msg='jQuery undefined (waiting time: %s sec)' % JQUERY_LOAD_TIME
        )
        ajax_script = 'return jQuery.active == 0;'
        wait_until(
            driver=driver,
            expression=lambda d: d.execute_script(ajax_script),
            seconds=AJAX_LOAD_TIME,
            msg='Ajax timeout (waiting time: %s sec)' % AJAX_LOAD_TIME
        )
    except TimeoutException as e:
        _check_browser_console(driver)
        raise PromiumTimeout(e.msg, AJAX_LOAD_TIME)


def wait_for_animation(driver):
    """Waits for execution animation"""
    enable_jquery(driver)
    jquery_script = 'return jQuery(":animated").length == 0;'
    return wait_until(
        driver=driver,
        expression=lambda d: d.execute_script(jquery_script),
        seconds=ANIMATION_LOAD_TIME,
        msg='Animation timeout (waiting time: %s sec)' % ANIMATION_LOAD_TIME
    )


def wait_for_page_loaded(driver):
    """Waits for page loaded"""
    try:
        current_url = driver.current_url
        if all(x not in current_url for x in (
            'facebook', 'moderation_panel', 'google'
        )):
            wait_for_ajax(driver)
            wait_for_animation(driver)
    except UnexpectedAlertPresentException as e:
        alert_is_present = EC.alert_is_present()
        if alert_is_present(driver):
            driver.switch_to_alert()
            alert = driver.switch_to_alert()
            e.alert_text = alert.text
            if e.alert_text == "Stop downloading new page?":
                pass
            else:
                alert.dismiss()
                raise e


def wait_for_alert(driver, seconds=10):
    """Wait fo alert"""
    return WebDriverWait(
        driver, seconds, ignored_exceptions=[WebDriverException]
    ).until(
        EC.alert_is_present(), "Alert is not present."
    )


def wait_for_alert_is_displayed(driver):
    try:
        wait_for_alert(driver)
    except TimeoutException:
        return False
    return True


def wait_for_status_code(url, status_code=200, tries=10):
    """Waits for status code"""
    for _ in range(tries):
        response = requests.get(url, verify=False)
        if response.status_code == status_code:
            return response
        time.sleep(1)
    raise PromiumException('')


def wait_until_new_window_is_opened(driver, original_window, window_num=0):
    wait_until(
        driver,
        lambda x: len(driver.window_handles) >= 2,
        msg='New window was not opened.'
    )
    window_handles = driver.window_handles
    window_handles.remove(original_window)
    return window_handles[window_num]


def wait_part_appear_in_class(driver, obj, part_class, msg=None):
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda driver: (part_class in obj.get_attribute('class')),
        seconds=5,
        msg=msg
    )


def wait_part_disappear_in_class(driver, obj, part_class, msg=None):
    if not msg:
        msg = f'"{part_class}" not present in attribute *class*.'
    wait_until(
        driver,
        lambda driver: (part_class not in obj.get_attribute('class')),
        seconds=5,
        msg=msg
    )


def wait_url_contains(driver, text, msg=None, timeout=5):
    if not msg:
        msg = f'"{text}" not present in url.'
    wait_until(driver, EC.url_contains(text), seconds=timeout, msg=msg)


def wait_url_not_contains(driver, text, msg=None, timeout=5):
    if not msg:
        msg = f'"{text}" not disappear in url.'
    wait_until_not(driver, EC.url_contains(text), seconds=timeout, msg=msg)
