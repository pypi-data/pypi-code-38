import os
import pytest
import logging
import threading
import requests
import traceback
import uuid
import time

from collections import namedtuple
from urllib.parse import urlsplit
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.opera.options import Options as OperaOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.remote.remote_connection import RemoteConnection

from promium.assertions import (
    WebDriverSoftAssertion,
    RequestSoftAssertion
)
from promium.exceptions import PromiumException
from promium.device_config import CHROME_DESKTOP_1920_1080
from promium.logger import (
    request_logging,
    logger_for_loading_page
)
from promium.common import upload_screenshot
from promium.kibana_search import get_kibana_link_for_one_test

TEST_PROJECT = os.environ.get('TEST_PROJECT')
TEST_CASE = os.environ.get('TEST_CASE')

log = logging.getLogger(__name__)

DRIVERS = {
    'firefox': 'Firefox',
    'chrome': 'Chrome',
    'safari': 'Safari',
    'opera': 'Opera',
    'ie': 'Ie',
}

MAX_LOAD_TIME = 10

DOWNLOAD_PATH = "/Downloads"


def get_chrome_opera_options(
        options, device, proxy_server=None, is_headless=False):
    if proxy_server:
        options.add_argument(f"--proxy-server={proxy_server}")
    if is_headless:
        options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--no-first-run")
    options.add_argument("--verbose")
    options.add_argument("--enable-logging --v=1")
    options.add_argument("--test-type")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={device.width},{device.height}")
    prefs = {
        "download.default_directory": DOWNLOAD_PATH,
        "download.directory_upgrade": True,
        'prompt_for_download': False
    }
    options.add_experimental_option("prefs", prefs)
    if device.user_agent:
        options.add_argument(f"--user-agent={device.user_agent}")
        if device.device_name:
            mobile_emulation = {"deviceName": device.device_name}
            options.add_experimental_option(
                "mobileEmulation", mobile_emulation
            )
    return options


def get_chrome_options(device, proxy_server=None, is_headless=False):
    options = ChromeOptions()
    chrome_options = get_chrome_opera_options(
        options, device, proxy_server, is_headless
    )
    return chrome_options


def get_opera_options(device, proxy_server=None):
    options = OperaOptions()
    opera_options = get_chrome_opera_options(options, device, proxy_server)
    opera_options.add_extension("/work/uaprom/res/WebSigner_v1.0.8.crx")
    opera_options.binary_location = '/usr/bin/opera'
    return opera_options


def get_firefox_profile(device):
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.startup.homepage", "about:blank")
    profile.set_preference("startup.homepage_welcome_url", "about:blank")
    profile.set_preference(
        "startup.homepage_welcome_url.additional", "about:blank"
    )
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
    profile.set_preference(
        "browser.helperApps.neverAsk.saveToDisk",
        "application/zip"
    )
    profile.set_preference("pdfjs.disabled", True)
    profile.set_preference("extensions.firebug.allPagesActivation", "on")
    profile.set_preference("extensions.firebug.console.enableSites", "on")
    profile.set_preference(
        "extensions.firebug.defaultPanelName", "console"
    )
    profile.set_preference(
        "extensions.firebug.console.defaultPersist", "true"
    )
    profile.set_preference(
        "extensions.firebug.consoleFilterTypes", "error"
    )
    profile.set_preference("extensions.firebug.showFirstRunPage", False)
    profile.set_preference("extensions.firebug.cookies.enableSites", True)
    if device.user_agent:
        profile.set_preference("general.useragent.override", device.user_agent)
    profile.update_preferences()
    return profile


def get_firefox_options(device):
    """Function available if selenium version > 2.53.0"""
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("-no-remote")
    firefox_options.add_argument(f"-width {device.width}")
    firefox_options.add_argument(f"-height {device.height}")
    return firefox_options


def create_driver(
        device, proxy_server=None, env_var='SE_DRIVER', default='chrome://'
):
    """
    Examples:

        - 'chrome://'
        - 'firefox://'
        - 'opera://'

    """
    is_headless = True if os.environ.get("HEADLESS") == "Enabled" else False
    browser_profile = None
    certs = {
        'acceptSslCerts': True,
        'acceptInsecureCerts': True
    }
    proxy_capabilities = Proxy(
        {
            "proxyType": ProxyType.DIRECT
        }
    )
    
    driver_dsn = os.environ.get(env_var) or default
    if not driver_dsn:
        raise RuntimeError(f'Selenium WebDriver is not set in the {env_var} '
                           f'environment variable')
    
    try:
        scheme, netloc, url, _, _ = urlsplit(driver_dsn)
    except ValueError:
        raise ValueError(f'Invalid url: {driver_dsn}')
    if scheme in DRIVERS:
        if scheme == "chrome":
            chrome_options = get_chrome_options(
                device, proxy_server, is_headless
            )
            return webdriver.Chrome(
                chrome_options=chrome_options,
                desired_capabilities=certs if is_headless else None
            )
        elif scheme == "firefox":
            return webdriver.Firefox(
                firefox_profile=get_firefox_profile(device),
                firefox_options=get_firefox_options(device)
            )
        elif scheme == "opera":
            return webdriver.Opera(options=get_opera_options(device))
        return getattr(webdriver, DRIVERS[scheme])()
    elif scheme.startswith('http+'):
        proto, _, client = scheme.partition('+')
        if not netloc:
            raise ValueError(f'Network address is not specified: {driver_dsn}')
        
        capabilities = getattr(DesiredCapabilities, client.upper(), None)
        capabilities["loggingPrefs"] = {
            "performance": "ALL", "server": "ALL", "client": "ALL",
            "driver": "ALL", "browser": "ALL"
        }
        if capabilities is None:
            raise ValueError(f'Unknown client specified: {client}')
        
        remote_url = f'{proto}://{netloc}{url}'
        command_executor = RemoteConnection(
            remote_url, keep_alive=False, resolve_ip=False
        )
        if client == "chrome":
            chrome_options = get_chrome_options(
                device, proxy_server, is_headless
            )
            chrome_options.add_argument("--disable-dev-shm-usage")
            capabilities.update(chrome_options.to_capabilities())
            if is_headless:
                capabilities.update(certs)
        elif client == "firefox":
            capabilities.update(get_firefox_options(device).to_capabilities())
            browser_profile = get_firefox_profile(device)
        elif client == "opera":
            capabilities.update(get_opera_options(device).to_capabilities())
            capabilities["browserName"] = "opera"
        if proxy_server:
            proxy_capabilities = Proxy(
                {
                    "httpProxy": proxy_server,
                    'sslProxy': proxy_server,
                    'noProxy': None,
                    "proxyType": ProxyType.MANUAL
                }
            )
        try:
            driver = webdriver.Remote(
                proxy=proxy_capabilities,
                command_executor=command_executor,
                desired_capabilities=capabilities,
                browser_profile=browser_profile
            )
        except WebDriverException:
            log.warning(
                "[PROMIUM] Second attempt for remote driver connection."
            )
            driver = webdriver.Remote(
                proxy=proxy_capabilities,
                command_executor=command_executor,
                desired_capabilities=capabilities,
                browser_profile=browser_profile
            )
        return driver
    
    raise ValueError(f'Unknown driver specified: {driver_dsn}')


class TDPException(Exception):
    
    def __init__(self, *args):
        self.message = (
            "exception caught during execution test data preparing.\n"
            "Look at the original traceback:\n\n%s\n"
            ) % ("".join(traceback.format_exception(*args)))
    
    def __str__(self):
        return self.message


class TDPHandler:
    """
    TDP - Test Data Preparation
    context manager for handling any exception
    during execution test data preparing.
    We need to raise a specific custom exceptions.
    :example:
    with self.tdp_handler():
        some code
    """
    
    def __init__(self):
        pass
    
    def __enter__(self):
        log.info("[TDP] Start test data preparing...")
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        log.info("[TDP] Finish test data preparing")
        if exc_type:
            raise TDPException(exc_type, exc_value, exc_tb)
        return


class TestCase(object):
    xrequestid = None
    test_case_url = None
    assertion_errors = None
    proxy_server = None
    
    def tdp_handler(self):
        """
        Use this context manager for prepare of test data only,
        not for business logic!
        """
        return TDPHandler()

    def get_kibana_link(self):
        attempts = 16  # 8 seconds
        while attempts:
            result = get_kibana_link_for_one_test(self.xrequestid)
            if result:
                self.xrequestid = None
                return result
            time.sleep(.5)
            attempts -= 1
        self.xrequestid = None
    
    def get_path_to_test(self, method):
        path = '/'.join(str(self.__class__).split('.')[1:-1])
        return f"{path}.py -k {method.__name__}"
    
    def get_failed_test_command(self):
        enviroment = "undefined"
        local = ""
        if TEST_PROJECT:
            enviroment = TEST_PROJECT
            local = '-local'
        return (
            f"vagga se --{enviroment}{local} "
            f"-- uaprom/{self.path_to_test} --capturelog --fail-debug-info"
        )


class WebDriverTestCase(TestCase, WebDriverSoftAssertion):
    driver = None
    device = CHROME_DESKTOP_1920_1080  # default data
    excluded_browser_console_errors = []

    ALLOWED_HOSTS = []
    SKIPPED_HOSTS = []
    
    FailInfoSelenium = namedtuple('FailInfoSelenium', [
        'test_type', 'url', 'screenshot', 'test_case', 'run_command', 'txid'
    ])
    
    @logger_for_loading_page
    def get_url(self, url, cleanup=True):
        self.driver.get(url)
        if cleanup:
            try:
                self.driver.execute_script(
                    'localStorage.clear()'
                )
            except WebDriverException:
                pass
        return url
    
    def check_console_errors(self):
        
        if hasattr(self.driver, "console_errors"):
            if self.driver.console_errors:
                browser_console_errors = self.driver.console_errors
                if self.excluded_browser_console_errors:
                    try:
                        return list(map(
                            lambda x: x, filter(
                                lambda x: x if not filter(
                                    lambda e: (
                                        True if e["msg"] in x and e["comment"]
                                        else False
                                    ),
                                    self.excluded_browser_console_errors
                                ) else None, browser_console_errors
                            )
                        ))
                    except Exception as e:
                        raise PromiumException(
                            "Please check your excluded errors list. "
                            "Original exception is: %s" % e
                        )
                return browser_console_errors
        return []
    
    def setup_method(self, method):
        self.assertion_errors = []
        pytest.config.get_fail_debug = self.get_fail_debug
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.check_console_errors = self.check_console_errors
        pytest.config.get_screenshot_png = self.get_screenshot_png
        self.path_to_test = self.get_path_to_test(method)
        
        if hasattr(method, 'device'):
            self.device = method.device.args[0]

        self.driver = create_driver(
            self.device, proxy_server=self.proxy_server
        )
        self.driver.xrequestid = self.xrequestid
        self.driver.console_errors = []
    
    def teardown_method(self, method):
        
        self.xrequestid = None
        self.driver.console_errors = []
        if self.driver:
            self.driver.xrequestid = None
            try:
                self.driver.quit()
            except WebDriverException as e:
                log.error(
                    "[PROMIUM] Original webdriver exception: %s" % e
                )
        if TEST_CASE == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")
    
    def get_screenshot_png(self):
        return self.driver.get_screenshot_as_png()
    
    def get_fail_debug(self):
        """Failed test report generator"""
        
        alerts = 0
        try:
            while self.driver.switch_to.alert:
                alert = self.driver.switch_to.alert
                print('Unexpected ALERT: %s\n' % alert.text)
                alerts += 1
                alert.dismiss()
        except Exception:
            if alerts != 0:
                print('')
            pass
        url = self.driver.current_url
        screenshot = upload_screenshot(self.driver)
        return self.FailInfoSelenium(
            test_type='selenium',
            url=(url, [None])[0],
            screenshot=(screenshot, [None])[0],
            test_case=(self.test_case_url, [None])[0],
            run_command=(self.get_failed_test_command(), [None])[0],
            txid=(self.xrequestid, [None])[0],
        )


class RequestTestCase(TestCase, RequestSoftAssertion):
    session = None
    proxies = {}
    
    FailInfoRequest = namedtuple(
        'FailInfoRequest',
        [
            'test_type',
            'url',
            'test_case',
            'status_code',
            'run_command',
            'txid'
        ]
    )
    
    def setup_method(self, method):
        self.session = requests.session()
        self.session.url = (
            'Use self.get_response(url) for request tests or '
            'util methods for api tests!'
        )
        self.assertion_errors = []
        pytest.config.assertion_errors = self.assertion_errors
        pytest.config.get_fail_debug = self.get_fail_debug
        self.path_to_test = self.get_path_to_test(method)
    
    def teardown_method(self, method):
        
        if self.session:
            self.session.close()
        
        if TEST_CASE == "True" and not self.test_case_url:
            raise PromiumException("Test don't have a test case url.")
        
        self.xrequestid = None
    
    def get_fail_debug(self):
        if not hasattr(self.session, 'status_code'):
            self.session.status_code = None
        
        """Failed test report generator"""
        return self.FailInfoRequest(
            test_type='request',
            url=(self.session.url, [None])[0],
            test_case=(self.test_case_url, [None])[0],
            status_code=(self.session.status_code, [None])[0],
            run_command=(self.get_failed_test_command(), [None])[0],
            txid=(self.xrequestid, [None])[0],
        )
    
    def get_response(self, url, method="GET", timeout=10, **kwargs):
        self.session.url = url
        self.session.status_code = None
        response = self.session.request(
            method=method,
            url=url,
            timeout=timeout,
            verify=False,
            cookies=dict(xrequestid=self.xrequestid),
            hooks=dict(response=request_logging),
            **kwargs,
        )
        self.session.status_code = response.status_code
        return response
