from selenium.webdriver import Chrome, Firefox, Ie, PhantomJS
from selenium.common.exceptions import TimeoutException

from umdriver.pages import LoginPage


class UMDriver(Chrome, Firefox, Ie, PhantomJS):

    URLS = {'prod': 'https://weblogin.umich.edu',
            'test': 'https://weblogin-test.itcs.umich.edu/'}

    def __init__(self, driver='chrome', **kwargs):
        if driver.lower() == 'chrome':
            Chrome.__init__(self, **kwargs)
        elif driver.lower() == 'ie':
            Ie.__init__(self, **kwargs)
        elif driver.lower() == 'firefox':
            Firefox.__init__(self, **kwargs)
        else:
            PhantomJS.__init__(self, **kwargs)

    def login(self, username, password, env='prod'):
        """Log in to UMich authenticated resources.

        Parameters
        ----------
        username : str
            UMich uniqname/username
        password : str
            Password
        env : ['prod', 'test'] (optional)
           The login environment to use.
        """
        url = self.URLS[env]
        self.get(url)
        page = LoginPage(self)
        page.username = username
        page.password = password
        page.submit()
