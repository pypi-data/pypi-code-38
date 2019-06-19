import re
import json
import requests

from typing import Dict, Optional
from json_checker import Checker, CheckerError

from promium.common import upload_screenshot


CoerceDict = Optional[Dict[str, type]]


def base_msg(msg):
    return f"{msg}\n" if msg else ""


def _check_namedtuple(obj):
    if hasattr(obj, "_asdict"):
        return obj._asdict()
    return obj


def convert_container(container):
    if not isinstance(container, str):
        return json.dumps(
            obj=container,
            indent=4,
            sort_keys=True,
            ensure_ascii=False,
            default=lambda obj: str(obj)
        )
    return _check_namedtuple(container)


def get_text_with_ignore_whitespace_symbols(text):
    """Return text excluding spaces and whitespace_symbols"""
    text_without_whitespace_symbols = (
        text
        .replace('\t', ' ')
        .replace('\v', ' ')
        .replace('\r', ' ')
        .replace('\n', ' ')
        .replace('\f', ' ')
        .strip()
    )
    text_list = text_without_whitespace_symbols.split(' ')
    text_list_without_space = [word for word in text_list if word]
    needful_text = ' '.join(text_list_without_space)
    return needful_text


class BaseSoftAssertion(object):

    # TODO is not cleaned in unit tests need use __init__
    assertion_errors = []

    def soft_assert_true(self, expr, msg=None):
        """Check that the expression is true."""
        if not expr:
            error = "Is not true." if not msg else msg
            self.assertion_errors.append(error)
            return error

    def soft_assert_false(self, expr, msg=None):
        """Check that the expression is false."""
        if expr:
            message = "Is not false." if not msg else msg
            self.assertion_errors.append(message)
            return message

    def soft_assert_equals(self, current, expected, msg=None):
        """Just like self.soft_assert_true(current == expected)"""
        message = (
            f"Current and expected has different data types: "
            f"current is {type(current)}, expected is {type(expected)}\n"
            if type(current) != type(expected) else ""
        )
        assert_message = (
            f"{'-' * 46}"
            f"\n{base_msg(msg)}\n"
            f"Current - {convert_container(current)}\n"
            f"Expected - {convert_container(expected)}\n"
            f"{message}"
            f"{'-' * 46}"
        )
        return self.soft_assert_true(current == expected, assert_message)

    def soft_assert_not_equals(self, current, expected, msg=None):
        """Just like self.soft_assert_true(current != expected)"""
        message = (
            f"{base_msg(msg)}"
            f"Current - {convert_container(current)}\n"
            f"Expected - {convert_container(expected)}\n"
        )
        self.soft_assert_false(current == expected, message)

    def soft_assert_in(self, member, container, msg=None):
        """Just like self.soft_assert_true(member IN container)"""
        msg = (
            f"{base_msg(msg)}"
            f"{member} not found in {convert_container(container)}\n"
        )
        return self.soft_assert_true(member in container, msg)

    def soft_assert_not_in(self, member, container, msg=None):
        """Just like self.soft_assert_true(member NOT IN container)"""
        msg = (
            f"{base_msg(msg)}"
            f"{member} unexpectedly found in {convert_container(container)}\n"
        )
        return self.soft_assert_true(member not in container, msg)

    def soft_assert_less_equal(self, a, b, msg=None):
        """Just like self.soft_assert_true(a <= b)"""
        error = f"{base_msg(msg)}{a} not less than or equal to {b}\n"
        return self.soft_assert_true(a <= b, error)

    def soft_assert_less(self, a, b, msg=None):
        """Just like self.soft_assert_true(a < b)"""
        error = f"{base_msg(msg)}{a} not less than {b}\n"
        return self.soft_assert_true(a < b, error)

    def soft_assert_greater_equal(self, a, b, msg=None):
        """Just like self.soft_assert_true(a >= b)"""
        error = f"{base_msg(msg)}{a} not greater than or equal to {b}\n"
        return self.soft_assert_true(a >= b, error)

    def soft_assert_greater(self, a, b, msg=None):
        """Just like self.soft_assert_true(a > b)"""
        error = f"{base_msg(msg)}{a} not greater than {b}\n"
        return self.soft_assert_true(a > b, error)

    def soft_assert_regexp_matches(self, text, expected_regexp, msg=None):
        """Fail the test unless the text matches the regular expression."""
        pattern = re.compile(expected_regexp)
        result = pattern.search(text)

        if not result:
            error = (
                f"{base_msg(msg)}"
                f"Regexp didn't match."
                f"Pattern {str(pattern.pattern)} not found in {str(text)}\n"
            )
            self.assertion_errors.append(error)
            return error

    def soft_assert_disable(self, element, msg=None):
        """Check that the obj hasn't attribute."""
        default_msg = f"Not disabled {element}\n" if not msg else ""
        error = f"{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(element.get_attribute("disabled"), error)

    def soft_assert_is_none(self, obj, msg=None):
        """Same as self.soft_assert_true(obj is None)."""
        default_msg = f"{obj} is not None.\n" if not msg else ""
        error = f"{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(obj is None, error)

    def soft_assert_is_not_none(self, obj, msg=None):
        """Included for symmetry with self.soft_assert_is_none."""
        default_msg = u"Unexpectedly None.\n" if not msg else u""
        error = f"{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(obj is not None, error)

    def soft_assert_is_instance(self, obj, cls, msg=None):
        """Same as self.soft_assert_true(isinstance(obj, cls))"""
        default_msg = (
            f"{obj} is not an instance of {cls}.\n" if not msg else ""
        )
        error = f"{base_msg(msg)}{default_msg}"
        return self.soft_assert_true(isinstance(obj, cls), error)

    def soft_assert_equals_text_with_ignore_spaces_and_register(
        self,
        current_text,
        expected_text,
        msg='Invalid checked text.'
    ):
        """Checking of text excluding spaces and register"""
        current = get_text_with_ignore_whitespace_symbols(current_text)
        expected = get_text_with_ignore_whitespace_symbols(expected_text)
        if not current:
            msg = "Warning: current text is None!"
        self.soft_assert_equals(
            current.lower(),
            expected.lower(),
            f"{msg}\nCurrent text without formating: {current_text}"
            f"\nExpected text without formating: {expected_text}"
        )

    def soft_assert_schemas(self, current, expected, msg=''):
        """
        Example:
            {'test1': 1} == {'test1: int}

        :param dict current: current response
        :param dict expected: expected dict(key: type)
        :param str msg:
        :return error
        """
        try:
            Checker(expected, soft=True).validate(current)
        except CheckerError as e:
            error = f'{msg}\n{e}'
            self.assertion_errors.append(error)
            return error

    def assert_keys_and_instances(
        self,
        actual_dict,
        expected_dict,
        can_be_null=None,
        msg=None
    ):
        """
        :param dict actual_dict:
        :param dict expected_dict:
        :param list | None can_be_null: must be if default value None
        :param basestring msg:
        """
        assert actual_dict, 'Actual dict is empty, check your data'

        self.soft_assert_equals(
            sorted(iter(actual_dict.keys())),
            sorted(iter(expected_dict.keys())),
            'Wrong keys list.'
        )
        for actual_key, actual_value in actual_dict.items():
            self.soft_assert_in(
                member=actual_key,
                container=expected_dict,
                msg=f'Not expected key "{actual_key}".'
            )
            if actual_key in expected_dict:
                expected_value = (
                    type(None) if
                    actual_value is None and
                    actual_key in (can_be_null or []) else
                    expected_dict[actual_key]
                )
                message = f'({msg})' if msg else ''
                self.soft_assert_true(
                    expr=isinstance(actual_value, expected_value),
                    msg=(
                        f'Wrong object instance class.\n'
                        f'Key "{actual_key}" value is "{type(actual_value)}", '
                        f'expected "{expected_value}". {message}'
                    )
                )

    def soft_assert_dicts_with_ignore_types(self, current, expected, msg=''):
        expected_dict = _check_namedtuple(expected)
        current_dict = _check_namedtuple(current)
        errors = ''
        for actual_key, actual_value in current_dict.items():
            if actual_key in expected_dict:
                if str(actual_value) != str(expected_dict[actual_key]):
                    errors += (
                        f"\nKey {actual_key} "
                        f"\nHas not correct value:  {actual_value}  "
                        f"Must be have this:  {expected_dict[actual_key]} \n"
                    )
        if errors:
            msg += (
                f'{errors}'
                f"\nExpected dict: {convert_container(expected_dict)}"
                f"\nCurrent dict: {convert_container(current_dict)}"
            )
            self.assertion_errors.append(msg)

    def soft_assert_equal_dict_from_clerk_magic(
        self,
        current_dict,
        expected_dict,
        msg=None,
        coerce: CoerceDict = None
    ):
        """
        Comparison by type, if the types do not match - compares in a string
        If the dict key was lost, print him in missing list.
        """
        def _equal(
                field_name: str,
                current: str, expected: str,
                type_coerce: CoerceDict
        ):
            if type_coerce is not None and field_name in type_coerce:
                cast = type_coerce[field_name]
                return cast(current) == cast(expected)
            elif type(current) == type(expected):
                return current == expected
            else:
                return str(current) == str(expected)

        missing = []
        unequal = []
        for key, value in expected_dict.items():
            if key not in current_dict:
                missing.append((key, value))
            elif not _equal(key, value, current_dict[key], coerce):
                unequal.append((
                    key, f"\n\t\tproduct_data - '{value}'"
                         f" != clerk_data - '{current_dict[key]}'"
                ))
        self.soft_assert_true(
            (missing, unequal) == ([], []),
            msg=(
                u"{base_msg}\n"
                u"Unequal_keys:\n\t{unequal}\n"
                u"\nMissed_keys:\n\t[{missing}]".format(
                    base_msg=base_msg(msg),
                    unequal='\n\t'.join(
                        [u":".join(map(str, a)) for a in unequal]
                    ),
                    missing='\n\t'.join(
                        [u":".join(map(str, a)) for a in missing]
                    ),
                )
            )
        )


class RequestSoftAssertion(BaseSoftAssertion):

    @property
    def url(self):
        return self.session.url

    def base_msg(self, msg=None):
        url = f"\n{self.url}" if self.url else ""
        exception = f"\n{msg}" if msg else ""
        return f"{url}{exception}"


class WebDriverSoftAssertion(BaseSoftAssertion):

    @property
    def driver(self):
        return self.driver

    @property
    def url(self):
        return self.driver.current_url

    @property
    def assertion_screenshot(self):
        return upload_screenshot(self.driver)

    def base_msg(self, msg=None):
        msg = f"\n{msg}" if msg else ""
        return f"\n{self.url}\nScreenshot - {self.assertion_screenshot}{msg}"

    def soft_assert_page_title(self, expected_title, msg=None):
        if not msg:
            msg = "Wrong page title."
        self.soft_assert_equals(self.driver.title, expected_title, msg)

    def soft_assert_current_url(self, expected_url, msg=None):
        if not msg:
            msg = "Wrong current url."
        self.soft_assert_equals(self.url, expected_url, msg)

    def soft_assert_current_url_contains(self, url_mask, msg=None):
        if not msg:
            msg = f"URL {str(self.url)} doesn't contains {str(url_mask)}.\n"
        self.soft_assert_in(url_mask, self.url, msg)

    def soft_assert_current_url_not_contains(self, url_mask, msg=None):
        if not msg:
            msg = f"URL {repr(self.url)} contains {repr(url_mask)}."
        self.soft_assert_not_in(url_mask, self.url, msg)

    def soft_assert_element_is_present(self, element, msg=None):
        if not msg:
            msg = (
                f"Element {element.by}={element.locator} is not present "
                f"on page at current time.\n"
            )
        self.soft_assert_true(element.is_present(), msg)

    def soft_assert_element_is_not_present(self, element, msg=None):
        if not msg:
            msg = f"Element {element.by}={element.locator} is found on page.\n"
        self.soft_assert_false(element.is_present(), msg)

    def soft_assert_element_is_displayed(self, element, msg=None):
        if not msg:
            msg = (
                f"Element {element.by}={element.locator} is not visible"
                f" to a user.\n"
            )
        self.soft_assert_true(element.is_displayed(), msg)

    def soft_assert_element_is_not_displayed(self, element, msg=None):
        if not msg:
            msg = (
                f"Element {element.by}={element.locator} "
                f"is visible to a user.\n"
            )
        self.soft_assert_false(element.is_displayed(), msg)

    def soft_assert_element_displayed_in_viewport(self, element, msg=None):
        """This method checks that element is viewable in viewport"""
        element_in_viewport = self.driver.execute_script(
            """
            function elementInViewport(el) {
                var top = el.offsetTop;
                var left = el.offsetLeft;
                var width = el.offsetWidth;
                var height = el.offsetHeight;


                while(el.offsetParent) {
                el = el.offsetParent;
                top += el.offsetTop;
                left += el.offsetLeft;
                }

                return (
                    top >= window.pageYOffset &&
                    left >= window.pageXOffset &&
                    (top + height) <= (window.pageYOffset + window.innerHeight)
                    &&
                    (left + width) <= (window.pageXOffset + window.innerWidth)
                );
            }

            element = arguments[0];
            return elementInViewport(element);
            """, element.lookup()
        )

        if element_in_viewport is not True:
            error = (
                f"{base_msg(msg)}"
                f"\nElement {element.by}={element.locator} "
                f"not displayed in viewport\n"
            )
            self.assertion_errors.append(error)

    def soft_assert_image_status_code(
        self, image, timeout=2, status_code=200, msg=None
    ):
        if not image.get_attribute('src'):
            return self.assertion_errors.append(
                'Image does not have attribute "src"'
            )

        img_url = image.get_attribute('src')
        response = requests.get(img_url, timeout=timeout, verify=False)

        self.soft_assert_equals(
            response.status_code,
            status_code,
            msg=msg if msg else 'img status code != 200'
        )
