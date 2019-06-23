# http://stackoverflow.com/questions/13789235/how-to-initialize-singleton-derived-object-once
# https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
import getpass
import json
import os
import platform
from pprint import pprint

import jsoncfg


class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

class Config():

    PLATFORM = platform.system()
    USERNAME_OS = getpass.getuser()

    def __init__(s):
        if not s.ROOT_DIR:
            raise Exception('Must define ROOT_DIR first')
        ROOT_DIR = s.ROOT_DIR
        s.config = jsoncfg.load_config(ROOT_DIR + '/config.json')

        s.USE_SQLITE = s.USE_SQLITE if hasattr(s, 'USE_SQLITE') else True # Support SQLite and MySQL only, so True for SQLite, False for MySQL
        s.DATABASE_NAME = s.DATABASE_NAME if hasattr(s, 'DATABASE_NAME') else 'scrape_app' # Database Name
        s.DEFINITION_FILE = s.DEFINITION_FILE if (s, 'DEFINITION_FILE') else '' # Error if empty


        s.APP_PATH = ROOT_DIR + '/app'
        s.BIN_PATH = ROOT_DIR + '/app/bin'
        s.DIST_PATH = ROOT_DIR + '/dist'
        s.LOG_PATH = ROOT_DIR + '/log'

        s.CONFIG_PATH = ROOT_DIR + '/dist/config'
        s.EXCEL_PATH = ROOT_DIR + '/dist/_excel'

        # Custom this direct, because it really large file.
        s.HTML_PATH = s.HTML_PATH if hasattr(s, 'HTML_PATH') else ROOT_DIR + '/dist/_html'
        s.IMAGES_PATH = s.IMAGES_PATH if hasattr(s, 'IMAGES_PATH') else ROOT_DIR + '/dist/images'
        s.DATABASE_PATH = s.DATABASE_PATH if hasattr(s, 'DATABASE_PATH') else s.CONFIG_PATH + '/database'
        s.USER_PATH = s.USER_PATH if hasattr(s, 'USER_PATH') else os.path.expandvars("%userprofile%")

        s.USER_DESKTOP = s.USER_PATH + os.sep + 'Desktop'
        s.DOCUMENTS_PATH = s.USER_PATH + os.sep + 'Documents'

        BIN_PATH = s.BIN_PATH

        s.CHROME_EXECUTABLE_PATH = BIN_PATH + '/chromedriver.exe'
        s.FIREFOX_EXECUTABLE_PATH = BIN_PATH + '/geckodriver.exe'
        s.FIREFOX_32_EXECUTABLE_PATH = BIN_PATH + '/geckodriver32.exe'
        s.PHANTOMJS_EXECUTABLE_PATH = BIN_PATH + '/phantomjs.exe'

        s.MAC_CHROME_EXECUTABLE_PATH = BIN_PATH + '/chromedriver'
        s.MAC_FIREFOX_EXECUTABLE_PATH = BIN_PATH + '/geckodriver'
        s.MAC_PHANTOMJS_EXECUTABLE_PATH = BIN_PATH + '/phantomjs'

        # s.LINUX_CHROME_EXECUTABLE_PATH = BIN_PATH + '/linux_chromedriver'
        # s.LINUX_FIREFOX_EXECUTABLE_PATH = BIN_PATH + '/linux_geckodriver'
        # s.LINUX_PHANTOMJS_EXECUTABLE_PATH = BIN_PATH + '/linux_phantomjs'

    def get_images_path(self):
        return self.IMAGES_PATH

    def get_html_path(self):
        return self.HTML_PATH

    def get_desktop_path(self):
        return self.USER_DESKTOP

    @staticmethod
    def is_win():
        return Config.PLATFORM == 'Windows'

    @staticmethod
    def is_win_32():
        return Config.PLATFORM == 'x86'

    @staticmethod
    def is_mac():
        return Config.PLATFORM == 'Darwin'

    def get_config(self, name=None):
        if not name:
            return self.config

        if '.' in name:
            c = self.config
            for n_ in name.split('.'):
                c = c[n_]
            return c.value

        return self.config[name]

    def init_folder(self):
        self.create_default_config_json()
        for folder in [
            self.DIST_PATH,
            self.LOG_PATH,

            self.EXCEL_PATH,
            self.CONFIG_PATH,
            self.HTML_PATH,
            self.IMAGES_PATH,
            self.DATABASE_PATH,
        ]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print('INFO: Create success dir ', folder)

    def is_use_mysql(self):
        return not self.USE_SQLITE

    def to_production(self):
        if self.DEFINITION_FILE:
            import shutil
            shutil.copy(self.DEFINITION_FILE, self.DEFINITION_FILE.replace('.py', '_prod.py'))
            print('INFO: to production file')
        else:
            raise Exception('Please init DEFINITION_FILE = __file__ in definition_prod.py')

    def create_default_config_json(self):
        config = {"mysql": {"host": "127.0.0.1", "port": 3306, "user": "root", "pass": "root"}, "redis": {"host": "127.0.0.1", "port": 6379, "db": 5}, "rabbitmq": {"host": "localhost", "port": 5672, "user": "user", "pass": "bitnami"}}
        config_file = self.ROOT_DIR + '/config.json'
        if not os.path.exists(config_file):
            data = json.dumps(config, indent=4)
            f = open(config_file, 'w')
            f.write(data)
            f.close()
            print('INFO: write config.json file')

    def __str__(self):
        pprint(vars(self))
        return ''

