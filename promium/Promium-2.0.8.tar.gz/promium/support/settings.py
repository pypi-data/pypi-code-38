
import os

from selenium.webdriver import DesiredCapabilities, FirefoxProfile
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.ie.options import Options as IeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from promium.device_config import Device, CHROME_DESKTOP_1024_768


BASE_CAPABILITIES = {
    'loggingPrefs': {
        'performance': 'ALL',
        'server': 'ALL',
        'client': 'ALL',
        'driver': 'ALL',
        'browser': 'ALL',
    }
}


def get_download_path():
    return os.environ.get('DOWNLOAD_PATH', '/tmp')


class SettingsDrivers(object):

    @staticmethod
    def chrome():
        return SettingsChrome()

    @staticmethod
    def firefox():
        return SettingsFirefox()

    @staticmethod
    def opera():
        return SettingsOpera()

    @staticmethod
    def ie():
        return SettingsIE()

    @staticmethod
    def edge():
        return SettingsEDGE()

    @classmethod
    def get(cls, browser_name):
        name = browser_name.lower()
        if hasattr(cls, name):
            method = getattr(cls, name)
            return method()
        raise ValueError('Not correct browser name {}'.format(name))


class Base(object):
    driver_capabilities = {}
    binary_path = ''
    device = CHROME_DESKTOP_1024_768
    default_options = []
    user_options = []
    default_exp_options = {}
    user_exp_options = {}
    default_capabilities = BASE_CAPABILITIES.copy()
    user_capabilities = {}
    default_preferences = {}
    user_preferences = {}

    @classmethod
    def driver_options(cls):
        raise NotImplementedError

    @classmethod
    def options(cls):
        return cls.user_options or cls.default_options

    @classmethod
    def experimental_options(cls):
        return cls.user_exp_options or cls.default_exp_options

    @classmethod
    def capabilities(cls):
        return cls.user_capabilities or cls.default_capabilities

    @classmethod
    def preference(cls):
        return cls.user_preferences or cls.default_preferences

    @classmethod
    def set_device(cls, width, height, user_agent='', device_name=''):
        """
        Set browser windows size and user agent
        :param int width: for example 1024
        :param int height: for example 768
        :param str device_name: for example Nexus 5
        :param str user_agent: not required param
        :return: namedtuple
        """
        cls.device = Device(
            width=width,
            height=height,
            user_agent=user_agent,
            device_name=device_name
        )
        return cls.device

    @classmethod
    def set_options(cls, *args):
        """
        set browser option, not use default
        :param args: fot example --no-sandbox, --test-type, ...,
        :return: list[str]
        """
        cls.user_options.extend(args)
        return cls.user_options

    @classmethod
    def add_option(cls, option):
        """
        add browser options to default
        :param str option: for example --headless
        :return: list[str]
        """
        cls.default_options.append(option)
        return cls.default_options

    @classmethod
    def delete_option(cls, option):
        """
        deleted browser options from default
        :param str option: for example --verbose
        :return: list[str]
        """
        cls.default_options.remove(option)
        return cls.default_options

    @classmethod
    def set_windows_size(cls, device=None):
        if device:
            cls.set_device(*device)

        if cls.device.user_agent:
            cls.add_option(
                "--user-agent={}".format(cls.device.user_agent)
            )

        cls.add_option(
            "--window-size={},{}".format(cls.device.width, cls.device.height)
        )
        return cls.default_options

    @classmethod
    def get_options(cls):
        cls.set_windows_size()
        driver_options = cls.driver_options()
        for option in cls.options():
            driver_options.add_argument(option)

        for exp_key, exp_option in cls.experimental_options().items():
            driver_options.add_experimental_option(exp_key, exp_option)

        if cls.device.device_name:
            mobile_emulation = {"deviceName": cls.device.device_name}
            driver_options.add_experimental_option(
                "mobileEmulation", mobile_emulation
            )

        if os.getenv('HEADLESS') == 'Enabled':
            driver_options.set_headless(True)

        return driver_options

    @classmethod
    def get_capabilities(cls):
        cap = cls.driver_capabilities.copy()
        for key, value in cls.capabilities().items():
            cap[key] = value
        return cap

    @classmethod
    def set_preferences(cls, **kwargs):
        cls.user_preferences.update(kwargs)
        return cls.user_preferences

    @classmethod
    def update_preferences(cls, **kwargs):
        for key, value in kwargs.items():
            cls.default_preferences[key] = value
        return cls.default_preferences

    @classmethod
    def delete_preference(cls, key):
        cls.default_preferences.pop(key)
        return cls.default_preferences

    @classmethod
    def get_preferences(cls):
        return None

    def __str__(self):
        return self.__class__.__name__


class SettingsChrome(Base):
    driver_capabilities = DesiredCapabilities.CHROME
    binary_path = '/usr/bin/chromedriver'
    default_options = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--no-default-browser-check',
        '--dns-prefetch-disable',
        '--no-first-run',
        '--verbose',
        '--enable-logging --v=1',
        '--test-type',
        '--ignore-certificate-errors',
        '--disable-notifications',
        '--disable-gpu'
    ]
    default_exp_options = {
        'prefs': {
            'download.default_directory': get_download_path(),
            'download.directory_upgrade': True,
            'prompt_for_download': False
        }
    }

    @classmethod
    def driver_options(cls):
        return ChromeOptions()


class SettingsOpera(SettingsChrome):
    driver_capabilities = DesiredCapabilities.OPERA
    # TODO need fix
    # binary_path = '/usr/bin/operadriver'
    binary_path = '/usr/bin/opera'

    @classmethod
    def get_options(cls):
        cls.set_windows_size()
        driver_options = cls.driver_options()
        for option in cls.options():
            driver_options.add_argument(option)

        for exp_key, exp_option in cls.experimental_options().items():
            driver_options.add_experimental_option(exp_key, exp_option)

        if os.getenv('HEADLESS') == 'Enabled':
            driver_options.set_headless(True)

        driver_options._binary_location = cls.binary_path
        return driver_options


class SettingsFirefox(Base):
    driver_capabilities = DesiredCapabilities.FIREFOX
    binary_path = '/usr/bin/gekodriver'
    default_options = ['-no-remote', ]
    default_preferences = {
        "browser.startup.homepage": "about:blank",
        "browser.download.folderList": 2,
        "browser.download.manager.showWhenStarting": False,
        "browser.download.dir": get_download_path(),
        "browser.helperApps.neverAsk.saveToDisk": "application/zip",
        "startup.homepage_welcome_url": "about:blank",
        "startup.homepage_welcome_url.additional": "about:blank",
        "pdfjs.disabled": True,
    }

    @classmethod
    def driver_options(cls):
        return FirefoxOptions()

    @classmethod
    def set_windows_size(cls, device=None):
        if device:
            cls.set_device(*device)

        cls.add_option('-width {}'.format(cls.device.width))
        cls.add_option('-height {}'.format(cls.device.height))
        return cls.default_options

    @classmethod
    def get_options(cls):
        cls.set_windows_size()
        driver_options = cls.driver_options()
        for option in cls.options():
            driver_options.add_argument(option)

        if os.getenv('HEADLESS') == 'Enabled':
            driver_options.set_headless(True)

        return driver_options

    @classmethod
    def get_preferences(cls):
        profile = FirefoxProfile()
        for key, value in cls.preference().items():
            profile.set_preference(key=key, value=value)

        if cls.device.user_agent:
            profile.set_preference(
                key='general.useragent.override',
                value=cls.device.user_agent
            )
        profile.update_preferences()
        return profile


class SettingsIE(Base):
    driver_capabilities = DesiredCapabilities.INTERNETEXPLORER
    binary_path = '/usr/bin/iedriver'

    @classmethod
    def driver_options(cls):
        return IeOptions()

    @classmethod
    def get_options(cls):
        driver_options = cls.driver_options()
        for option in cls.options():
            driver_options.add_argument(option)

        return driver_options


class SettingsEDGE(Base):
    driver_capabilities = DesiredCapabilities.EDGE
    binary_path = '/usr/bin/edgedriver'

    @classmethod
    def driver_options(cls):
        return EdgeOptions()

    @classmethod
    def get_options(cls):
        return cls.driver_options()
