from functools import wraps

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def waitfunc(timeout=10):
    """
    Decorator that will wait for the processing spinner to disappear before and
    after the decorated function is called.

    This method assumes that a webdriver is the first positional argument in the function.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(driver, *args, **kwargs):
            wait = WebDriverWait(driver, timeout)
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "SAVED_")]')))
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "WAIT_")]')))
            r = fn(driver, *args, **kwargs)
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "SAVED_")]')))
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "WAIT_")]')))
            return r
        return wrapper
    return decorator


def waitmethod(timeout=10):
    """
    Decorator that will wait for the processing spinner to disappear before and
    after the decorated method is called.

    This decorator assumes that the instance of the method has a webdriver
    assigned to `self.d`.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(instance, *args, **kwargs):
            wait = WebDriverWait(instance.d, timeout)
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "SAVED_")]')))
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "WAIT_")]')))
            r = fn(instance, *args, **kwargs)
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "SAVED_")]')))
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//div[starts-with(@id, "WAIT_")]')))
            return r
        return wrapper
    return decorator
