
import logging
import os
import random
import time
import requests
from collections import Sequence

from functools import wraps

from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
    TimeoutException
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from promium.logger import (
    add_logger_to_base_element_classes,
    logger_for_loading_page
)
from promium.waits import wait_for_page_loaded, wait_until
from promium.expected_conditions import is_present
from promium.exceptions import (
    ElementLocationException,
    LocatorException,
    PromiumException
)


log = logging.getLogger(__name__)


MAX_TRIES = 20


def with_retries(tries, second_to_wait):
    """
    If element not found wait and try again
    If element found returned
    :param int tries:
    :param float second_to_wait: wait seconds
    :return: callable_func
    """

    def callable_func(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for t in range(tries):
                res = func(*args, **kwargs)
                if res:
                    return res
                time.sleep(second_to_wait)

            element = args[0]
            raise ElementLocationException(
                u'Element with %s=%s not found' % (element.by, element.locator)
            )

        return wrapper
    return callable_func


def highlight_element(func):
    """
    Enabled for debug only
    :param func:
    :return: wrapper
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        element = func(self, *args, **kwargs)
        highlight_status = os.environ.get('HIGHLIGHT')
        if highlight_status == 'Enabled':
            self.driver.execute_script("""
                element = arguments[0];
                original_style = element.getAttribute('style');
                element.setAttribute('style', original_style +
                ";border: 3px solid #D4412B;");
                setTimeout(function(){
                element.setAttribute('style', original_style);
                    }, 300);
                """, element)
            time.sleep(.5)
        return element
    return wrapper


def get_web_driver(driver):
    if isinstance(driver, WebDriver):
        return driver
    elif isinstance(driver, WebElement):
        return get_web_driver(driver._parent)
    error = u'Wrong driver instance. Supported WebDriver and WebElement only'
    raise PromiumException(error)


class Page(object):

    def __init__(self, driver):
        self._driver = driver

    url = None

    @property
    def driver(self):
        return self._driver

    def lookup(self):
        return None

    @logger_for_loading_page
    def open(self, **kwargs):
        if not self.url:
            raise PromiumException("Can't open page without url")
        self.driver.get(self.url.format(**kwargs))

    @logger_for_loading_page
    def refresh(self):
        self.driver.refresh()

    def wait_for_page_loaded(self):
        wait_for_page_loaded(self.driver)

    def wait_for_source_changed(self, action_func, *args, **kwargs):
        source = self.driver.page_source
        action_func(*args, **kwargs)
        wait_until(
            self.driver, lambda driver: driver.page_source != source,
            msg="Page source didn't change."
        )

    def get_status_code(self):
        """ get status_code from current page """
        session = requests.Session()
        for cookie in self.driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        r = session.get(
            url=self.driver.current_url,
            timeout=5, verify=False, allow_redirects=False
        )
        session.close()
        return r.status_code


class Bindable(object):

    def bind(self, parent, driver, parent_cls=None):
        c = self.__class__.__new__(self.__class__)
        c.__dict__ = self.__dict__.copy()
        c.parent = parent
        c.parent_cls = parent_cls
        c.driver = driver
        return c

    def __get__(self, instance, owner):
        return self.bind(instance.lookup(), instance.driver, instance)


class Base(Bindable):

    def __init__(self, by, locator):
        self.by = by
        self.locator = locator

    index = 0
    parent = None
    driver = None
    parent_cls = None
    _cached_elements = None

    def _refresh_parent(self):
        if self.parent_cls:
            self.driver = self.parent_cls.driver
            self.parent = self.parent_cls.lookup()

    def _get_current_driver(self):
        """
        Returned WebDriver or WebElement
        :return: obj
        """
        obj = self.parent if self.parent is not None else self.driver
        return obj

    def _validate_locator(self):
        """
        Validate XPATH locators:
        locator mast have start "."
        for example ".//*[@id='cabinet']"
        :return tuple[str, str]
        """
        if isinstance(self._get_current_driver(), WebElement):
            if self.by == By.XPATH and not self.locator.startswith("."):
                raise LocatorException(
                    'Xpath locator must start with "." (dot). '
                    'Please check this locator "%s"' % self.locator
                )
        return self.by, self.locator

    def _find_elements(self):
        driver = self._get_current_driver()
        locator = self._validate_locator()
        try:
            self._cached_elements = driver.find_elements(*locator)
        except StaleElementReferenceException:
            self._refresh_parent()
            self._cached_elements = driver.find_elements(*locator)
        return self._cached_elements

    @with_retries(MAX_TRIES, .5)
    def _finder(self, force=False):
        """
        Used cache, find element only first call
        :return: self._cached_elements
        """
        if force or not self._cached_elements:
            self._find_elements()
        return self._cached_elements


class Collection(Base, Sequence):

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def get_item(self, index):
        item_name = self.base.__name__ + 'Item'
        params = {
            'parent': self.parent,
            'driver': self.driver,
            'parent_cls': self.base.parent_cls,
            '_cached_elements': self._cached_elements,
            'index': index
        }
        return type(item_name, (self.base, ), params)(self.by, self.locator)

    def __getitem__(self, val):
        if isinstance(val, slice):
            start = val.start or 0
            stop = val.stop if val.stop < len(self) else len(self)
            step = val.step or 1
            return [self.get_item(i) for i in range(start, stop, step)]

        return self.get_item(val)

    def __len__(self):
        return len(self._find_elements())

    def is_empty(self):
        return bool(len(self) < 1)

    def is_not_empty(self):
        return not self.is_empty()

    def random_choice(self):
        elements = self.wait_not_empty()
        index = random.randint(0, len(elements) - 1)
        return self.get_item(index)

    def wait_empty(self, timeout=10):
        msg = 'Collection with {}={} is not empty after {}'.format(
            self.by, self.locator, timeout
        )
        wait_until(self.driver, lambda e: self.is_empty(), timeout, msg)
        return self

    def wait_not_empty(self, timeout=10):
        msg = 'Collection with {}={} is empty after {}'.format(
            self.by, self.locator, timeout
        )
        wait_until(self.driver, lambda e: self.is_not_empty(), timeout, msg)
        return self

    def filter_by(self, child_locator):
        """
        Filtered blocks contained child CSS locator for example:
        Get product_blocks have buy_button
        :param str child_locator: example [data-qaid="buy_button"]
        """
        script = u"return $('{parent_locator}:has({child_locator})');".format(
            parent_locator=self.locator,
            child_locator=child_locator
        )
        results = self.driver.execute_script(script)
        if not results:
            ElementLocationException(
                'Not fond elements with %s' % child_locator
            )
        self._cached_elements = results
        return self

    def find_all(self, by, locator):
        """
        Changed locator for lookup
        :param str by: example By.CSS_SELECTOR
        :param str locator: example [data-qaid="some-locator"]
        :return: Collection
        """
        c = self.bind(self.parent, self.driver, self)
        c.by = by
        c.locator = locator
        return c

    def find(self, by, locator):
        """
        Changed locator for lookup
        :param str by: example By.CSS_SELECTOR
        :param str locator: example [data-qaid="some-locator"]
        :return: Element
        """
        return self.find_all(by, locator).get_item(0)

    def find_by_text(self, text, check_negative=False):
        found_elements_by_test = []
        for element in self:
            if self.driver.execute_script(
                    """
                    var el = arguments[0];
                    var text = arguments[1];
                    var element
                    var index;
                    if (el.innerText.includes(text)) element = true;
                    return element
                    """, element.lookup(), text
            ):
                found_elements_by_test.append(element)
        if len(found_elements_by_test) == 0:
            if check_negative:
                return False
            else:
                raise PromiumException(
                    'Element with text "%s" has not been found' % text
                )
        else:
            return found_elements_by_test[0]

    @property
    def first_item(self):
        return self.wait_not_empty().get_item(0)

    @property
    def last_item(self):
        return self.wait_not_empty().get_item(-1)


@add_logger_to_base_element_classes
class ElementBase(Base):

    def _get_element(self):
        if self.index >= len(self._cached_elements):
            raise PromiumException(
                'Collection by={by} locator={locator} has been changed, '
                'get {index} of {maximum} elements'.format(
                    by=self.by,
                    locator=self.locator,
                    index=self.index,
                    maximum=len(self._cached_elements) - 1
                )
            )
        return self._cached_elements[self.index]

    @highlight_element
    def lookup(self):
        wait_for_page_loaded(get_web_driver(self.driver))
        try:
            self._cached_elements = self._finder()
            element = self._get_element()
            element.is_displayed()
        except StaleElementReferenceException:
            self._refresh_parent()
            self._cached_elements = self._finder(force=True)
            element = self._get_element()
        return element

    @classmethod
    def as_list(cls, by, locator):
        params = {'parent': cls.parent, 'driver': cls.driver, 'base': cls}
        return type(cls.__name__ + 'List', (Collection, ), params)(by, locator)

    def wait_to_display(self, timeout=10):
        obj = self._get_current_driver()
        try:
            WebDriverWait(
                obj, timeout, ignored_exceptions=[WebDriverException]
            ).until(
                lambda driver: self.is_displayed(),
                "Element with %s=%s was found "
                "but was not displayed after %s seconds" % (
                    self.by, self.locator, timeout
                )
            )
            wait_for_page_loaded(self.driver)
            return self
        except TimeoutException as e:
            raise ElementLocationException(e.msg)

    def wait_to_present(self, timeout=10):
        obj = self._get_current_driver()
        params = (self.by, self.locator, timeout)
        msg = "Element with %s=%s not found after %s seconds" % params
        wait_until(obj, is_present(self), timeout, msg)
        return self

    def wait_to_disappear(self, time=10):
        def _find_no_visible_element(self):
            obj = self._get_current_driver()
            try:
                return not obj.find_element(
                    self.by, self.locator
                ).is_displayed()
            except (
                NoSuchElementException,
                StaleElementReferenceException,
                WebDriverException
            ):
                return True
        return WebDriverWait(self.driver, time).until(
            lambda driver: _find_no_visible_element(self),
            "Element with %s=%s did not disappear after %s seconds" % (
                self.by, self.locator, time
            )
        )

    def get_attribute(self, name):
        return self.lookup().get_attribute(name)

    def check_class_part_presence(self, class_name):
        return bool(class_name in self.lookup().get_attribute('class'))

    @property
    def location(self):
        return self.lookup().location

    def is_present(self):
        """Checks if element is present on page at current time"""
        try:
            return bool(self._find_elements())
        except WebDriverException as e:
            log.error(
                "[PROMIUM] Original webdriver exception: %s" % e
            )
            return False

    @property
    def text(self):
        return self.lookup().text

    def click(self):
        """ custom click, with blackjack and hookers """
        self.scroll_into_view()
        self.lookup().click()

    def js_click(self):
        self.driver.execute_script('arguments[0].click()', self.lookup())

    def is_displayed(self):
        return self.lookup().is_displayed()

    def hover_over(self):
        ActionChains(self.driver).move_to_element(self.lookup()).perform()

    def hover_over_with_offset(self, xoffset=1, yoffset=1):
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def click_with_offset(self, xoffset=1, yoffset=1):
        ActionChains(self.driver).move_to_element_with_offset(
            self.lookup(), xoffset, yoffset
        ).click().perform()

    def move_to_element_and_click(self):
        ActionChains(self.driver).move_to_element(
            self.lookup()).click().perform()

    @property
    def element_title(self):
        return self.get_attribute("title")

    @property
    def element_id(self):
        return self.get_attribute("id")

    def value_of_css_property(self, property_name):
        """ Returns the value of a CSS property """
        return self.lookup().value_of_css_property(property_name)

    def scroll_into_view(
        self, behavior="instant", block="center", inline="center"
    ):
        """
        Method scrolls the element on which it's called into the visible
        area of the browser window.

        element.scrollIntoView();
        element.scrollIntoView(scrollIntoViewOptions); // Object parameter

        :Args:
        - behavior - Defines the transition animation. One of "auto" or
            "smooth" or "instant".
        - block - Defines vertical alignment. One of "start", "center",
            "end", or "nearest".
        - inline - Defines horizontal alignment. One of "start", "center",
            "end", or "nearest".
        """
        options = {
            "behavior": behavior,
            "block": block,
            "inline": inline
        }
        self.driver.execute_script(
            'arguments[0].scrollIntoView(arguments[1]);',
            self.lookup(), options
        )
        return self

    def drag_and_drop(self, target):
        ActionChains(self.driver).drag_and_drop(
            self.lookup(), target.lookup()
        ).perform()


class Block(ElementBase):
    pass


class Element(ElementBase):

    @property
    def tag_name(self):
        """Gets this element's tagName property."""
        return self.lookup().tag_name

    def submit(self):
        """Submits a form."""
        return self.lookup().submit()

    def is_selected(self):
        """
        Can be used to check if a checkbox or radio button is selected.
        """
        return self.lookup().is_selected()

    def is_enabled(self):
        """Whether the element is enabled."""
        return self.lookup().is_enabled()

    @property
    def location_once_scrolled_into_view(self):
        """CONSIDERED LIABLE TO CHANGE WITHOUT WARNING.
        Use this to discover where on the screen an element is
        so that we can click it. This method should cause
        the element to be scrolled into view.

        Returns the top lefthand corner location on the screen,
        or None if the element is not visible
        """
        return self.lookup().location_once_scrolled_into_view

    @property
    def size(self):
        """ Returns the size of the element """
        return self.lookup().size

    @property
    def id(self):
        """ Returns internal id used by selenium.

        This is mainly for internal use.  Simple use cases such as checking
        if 2 webelements refer to the same element, can be done using '=='::

            if element1 == element2:
                print("These 2 are equal")

        """
        return self.lookup().id

    def wait_to_staleness(self):
        return wait_until(
            driver=self.driver,
            expression=EC.staleness_of(self.lookup()),
            seconds=10,
        )

    def wait_for_text_present(self, text):
        params = (self.by, self.locator)
        return wait_until(
            driver=self.driver,
            seconds=10,
            expression=EC.text_to_be_present_in_element(params, text),
            msg="Text: %s, does not appear after 10 seconds" % text
        )

    def set_inner_html(self, value):
        self.driver.execute_script(
            'arguments[0].innerHTML = "%s"' % value, self.lookup()
        )

    def hover_over_and_click(self, on_element=None):
        ActionChains(self.driver).move_to_element(self.lookup()).click(
            on_element.lookup()
        ).perform()

    def drag_and_drop_by_offset(self, xoffset, yoffset):
        ActionChains(self.driver).drag_and_drop_by_offset(
            self.lookup(), xoffset, yoffset
        ).perform()

    def wait_for_changes_text_attribute(self, name_attribute, text):
        return wait_until(
            driver=self.driver,
            expression=lambda driver: text != self.get_attribute(name_attribute),
            seconds=10,
            msg='Text attribute has not changed'
        )

    def wait_for_text_change(self, text=None):
        element_text = text or self.text
        return wait_until(
            driver=self.driver,
            expression=lambda driver: element_text != self.text,
            seconds=5,
            msg='Text "{}" not changed'.format(element_text)
        )

    def wait_to_enabled(self, time=10):
        try:
            wait = WebDriverWait(
                self.driver, time,
                ignored_exceptions=[WebDriverException])
            message = "Element with %s=%s not enabled after %s seconds" % (
                self.by, self.locator, time
            )
            return wait.until(
                lambda driver:
                False if self.get_attribute("disabled") == 'true'
                else self, message
            )
        except TimeoutException as e:
            raise ElementLocationException(e.msg)
