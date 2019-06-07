from selenium.common.exceptions import (ElementNotVisibleException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from umdriver.exceptions import LoginError


class LoginPage:
    """Page object for the UM Weblogin page."""
    URL = 'https://weblogin.umich.edu'
    LOCS = {
        'username': (By.ID, 'login'),
        'password': (By.ID, 'password'),
        'submit': (By.ID, 'loginSubmit'),
        'error_msg': (By.CSS_SELECTOR, 'div.alert-danger'),
        'helpblock_username': (By.ID, 'helpBlock-login'),
        'helpblock_password': (By.ID, 'helpBlock-password')
    }

    def __init__(self, driver):
        self.d = driver

    @property
    def username(self):
        el = self.d.find_element(*self.LOCS['username'])
        return el.get_attribute('value')

    @username.setter
    def username(self, value):
        el = self.d.find_element(*self.LOCS['username'])
        el.clear()
        el.send_keys(value + Keys.TAB)

    @property
    def password(self):
        el = self.d.find_element(*self.LOCS['password'])
        return el.get_attribute('value')

    @password.setter
    def password(self, value):
        el = self.d.find_element(*self.LOCS['password'])
        el.clear()
        el.send_keys(value + Keys.TAB)

    @classmethod
    def get(cls, driver):
        driver.get(cls.URL)
        return cls(driver)

    def _submit(self):
        """Click the submit button."""
        el = self.d.find_element(*self.LOCS['submit'])
        el.click()

    def submit(self):
        """Click the submit button and handle duo."""
        self._submit()
        if self.error_msgs:
            raise LoginError(self.error_msgs)
        wait = WebDriverWait(self.d, 180)
        print('Waiting for DUO authentication...')
        try:
            wait.until(lambda d: d.title != 'U-M Weblogin')
        except TimeoutException:
            print('Login failed.')
            raise
        else:
            print('Login successful.')

    @property
    def error_msgs(self):
        """Returns the present error message, if an error is present.

        Otherwise returns None.
        """
        errors = []
        # capture errors from alert dialog
        try:
            el = self.d.find_element(*self.LOCS['error_msg'])
        except (NoSuchElementException, ElementNotVisibleException):
            pass  # error is not present
        else:
            banner_error = el.text.strip()
            if banner_error != '':
                errors.append(banner_error)
        # capture errors from username helptext
        try:
            el = self.d.find_element(*self.LOCS['helpblock_username'])
        except (NoSuchElementException, ElementNotVisibleException):
            pass
        else:
            username_error = el.text.strip()
            if username_error != '':
                errors.append(username_error)
        # capture errors from password helptext
        try:
            el = self.d.find_element(*self.LOCS['helpblock_password'])
        except (NoSuchElementException, ElementNotVisibleException):
            pass
        else:
            password_error = el.text.strip()
            if password_error != '':
                errors.append(password_error)
            errors.append(el.text.strip())
        return errors
