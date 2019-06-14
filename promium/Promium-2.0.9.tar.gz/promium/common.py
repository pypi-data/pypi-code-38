
import os
import datetime
import urllib
import requests
import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from promium.waits import wait_for_page_loaded


def scroll_to_bottom(driver):
    """Scrolls down page"""
    driver.execute_script('jQuery("img.img-ondemand").trigger("appear");')
    wait_for_page_loaded(driver)
    driver.execute_script(
        """
        var f = function(old_height) {
            var height = $$(document).height();
            if (height == old_height) return;
            $$('html, body').animate({scrollTop:height}, 'slow', null,
            setTimeout(function() {f(height)}, 1000)
            );
        }
        f();
        """
    )


def scroll_to_top(driver):
    wait_for_page_loaded(driver)
    driver.execute_script(
        """jQuery('html, body').animate({scrollTop: 0 }, 'slow', null);"""
    )


def scroll_to_bottom_in_block(driver, element_class):
    script = """
        var elem = '.'.concat(arguments[0]);
        $(elem).animate({scrollTop: $(elem).prop('scrollHeight')}, 1000);
    """
    driver.execute_script(script, element_class)


def scroll_to_element(driver, element, base_element=None):
    """
    use base_element if you need for example scroll into popup,
    base_element must be a popup locator.
    """
    if base_element is None:
        base_element = 'html, body'
    script = """
        var elem = arguments[0];
        var base = arguments[1];
        var relativeOffset = (
            jQuery(elem).offset().top - jQuery(base).offset().top
        );
        jQuery(base).animate({
            scrollTop: relativeOffset
            }, 'slow', null
        );
             """
    wait_for_page_loaded(driver)
    driver.execute_script(script, element, base_element)


def scroll_with_offset(driver, element, with_offset=0):
    script = """
        var elem = arguments[0];
        jQuery('html, body').animate({
            scrollTop: jQuery(elem).offset().top + arguments[1]
            }, 'fast', null
        );
        """
    driver.execute_script(script, element, with_offset)


# TODO need implemented
def switch_to_window(driver, window_handle):
    """Switches to window"""
    driver.switch_to_window(window_handle)


def get_screenshot_path(name, with_date=True):
    now = datetime.datetime.now().strftime('%d_%H_%M_%S_%f')
    screenshot_name = f"{name}_{now}.png" if with_date else f"{name}.png"
    screenshots_folder = "/tmp"
    if not os.path.exists(screenshots_folder):
        os.makedirs(screenshots_folder)
    screenshot_path = os.path.join(screenshots_folder, screenshot_name)
    return screenshot_path, screenshot_name


def upload_screenshot(driver, path_name="screenshot", path_with_date=True):
    try:
        screenshot_path, screenshot_name = get_screenshot_path(
            name=path_name,
            with_date=path_with_date
        )
        driver.save_screenshot(screenshot_path)

        def read_in_chunks(img, block_size=1024, chunks=-1):
            """
            Lazy function (generator) to read a file piece by piece.
            Default chunk size: 1k.
            """
            while chunks:
                data = img.read(block_size)
                if not data:
                    break
                yield data
                chunks -= 1
        screenshot_url = f"https://screenshots.uaprom/{screenshot_name}"
        r = requests.put(
            url=screenshot_url,
            auth=('selenium', 'selenium'),
            data=read_in_chunks(open(screenshot_path, 'rb')),
            verify=False
        )
        os.remove(screenshot_path)
        if not r.ok:
            return (
                f"Screenshot not uploaded to server. "
                f"Status code: {r.status_code}, reason: {r.reason}"
            )
    except Exception as e:
        screenshot_url = (
            f'No screenshot was captured due to exception {repr(e)}'
        )
    return screenshot_url


def download_and_check_file(download_url, file_path):
    try:
        urllib.urlretrieve(download_url, file_path)
        if os.path.isfile(file_path) and os.path.exists(file_path):
            return True
        else:
            return False
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def control_plus_key(driver, key):
    """Imitations press CONTROL key + any key"""
    (
        ActionChains(driver)
        .key_down(Keys.CONTROL)
        .send_keys(key)
        .key_up(Keys.CONTROL)
        .perform()
    )


def set_local_storage(driver, key, value):
    """Sets value in browsers local storage"""
    driver.execute_script(
        "localStorage.setItem('%s', '%s')" % (key, value)
    )


def delete_cookie_item(driver, name):
    driver.delete_cookie(name)
    driver.refresh()


def delete_element_from_dom(driver, element):
    driver.execute_script(f"""
        var element = document.querySelector("{element}");
        if (element)
        element.parentNode.removeChild(element);
    """)


def scroll_into_end(driver, timeout=1):
    """Scroll block into end page"""
    driver.execute_script(
        'window.scrollTo(0, document.body.scrollHeight);'
    )
    time.sleep(timeout)
