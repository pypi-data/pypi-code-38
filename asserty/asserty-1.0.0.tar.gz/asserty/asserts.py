from unittest import TestCase
from typing import Any, Union


tc = TestCase("__init__")


def assert_true(obj, msg=""):
    tc.assertTrue(obj, msg)


def assert_false(obj, msg=""):
    tc.assertFalse(obj, msg)


def assert_none(obj, msg=""):
    tc.assertIsNone(obj, msg)


def assert_not_none(obj, msg=""):
    tc.assertIsNotNone(obj, msg)


def assert_equal(a, b, msg=""):
    tc.assertEqual(a, b, msg)


def assert_not_equal(a, b, msg=""):
    tc.assertNotEqual(a, b, msg)


def assert_greater_than(a, b, msg=""):
    tc.assertGreater(a, b, msg)


def assert_greater_equal_than(a, b, msg=""):
    tc.assertGreaterEqual(a, b, msg)


def assert_less_than(a, b, msg=""):
    tc.assertLess(a, b, msg)


def assert_less_equal_than(a, b, msg=""):
    tc.assertLessEqual(a, b, msg)


def assert_raises(err, func, *args, **kwargs):
    tc.assertRaises(err, func, *args, **kwargs)


def assert_type(obj, t, msg=""):
    tc.assertIsInstance(obj, t, msg)


def assert_not_type(obj, t, msg=""):
    tc.assertNotIsInstance(obj, t, msg)


def assert_contains(coll, obj, msg=""):
    tc.assertIn(obj, coll, msg)


def assert_not_contains(coll, obj, msg=""):
    tc.assertNotIn(obj, coll, msg)


class Assert:
    def __init__(self, value):
        self.value = value

    @property
    def also(self):
        """Make further assertions on this with AND between them."""
        return self

    and_do = also
    and_is = also

    def is_none(self):
        """Assert that this has a value of None."""
        msg = "Expected {} to be None".format(self.value)
        assert_none(self.value, msg)

    def is_not_none(self):
        """Assert that this DO NOT has a value of None."""
        msg = "Expected {} to be None".format(self.value)
        assert_not_none(self.value, msg)

    def equals(self, other):
        """Assert that if this object is equal to the other object."""
        msg = "Expected {} to equal".format(self.value, other)
        assert_equal(self.value, other, msg)
        return self

    def not_equals(self, other):
        """Check that if this object DO NOT equal to the other object."""
        msg = "Expected {} not to equal".format(self.value, other)
        assert_not_equal(self.value, other, msg)
        return self

    def has_type(self, expected):
        """Assert that this has the expected type."""
        if not isinstance(expected, type):
            expected = type(expected)
        msg = "Expected {} to have type {} but was {}".format(self.value, type(self.value), expected)
        assert_type(self.value, expected, msg)
        return self

    has_same_type_as = has_type
    is_instance = has_type

    def not_has_type(self, expected):
        """Assert that this NOT have the expected type."""
        if not isinstance(expected, type):
            expected = type(expected)
        msg = "Expected {} not to have type {} but was".format(self.value, expected)
        assert_not_type(self.value, expected, msg)
        return self

    not_has_same_type_as = not_has_type
    not_is_instance = not_has_type

    def is_in(self, coll):
        """Assert that this is in the given collection."""
        msg = "Expected {} to be in {} but was not".format(self.value, coll)
        assert_contains(coll, self.value, msg)
        return self

    def is_not_in(self, coll):
        """Assert that this is NOT in the given collection."""
        msg = "Expected {} not to be in {} but was".format(self.value, coll)
        assert_not_contains(coll, self.value, msg)
        return self

    def has_length(self, expected):
        """Assert that this is of the expected length"""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length {} but was {}".format(self.value, expected, len(self.value))
        assert_equal(len(self.value), expected, msg)
        return self

    def not_has_length(self, expected):
        """Assert that this is NOT of the expected length"""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length {} but was".format(self.value, expected)
        assert_not_equal(len(self.value), expected, msg)
        return self

    def is_greater_than(self, other):
        """Assert that this is greater than other."""
        msg = "Expected {} to be greater than {}".format(self.value, other)
        assert_greater_than(self.value, other, msg)
        return self

    def is_greater_or_equal_to(self, other):
        """Assert that this is greater than other."""
        msg = "Expected {} to be greater or equal to {}".format(self.value, other)
        assert_greater_equal_than(self.value, other, msg)
        return self

    def is_less_than(self, other):
        """Assert that this is greater than other."""
        msg = "Expected {} to be less than {}".format(self.value, other)
        assert_less_than(self.value, other, msg)
        return self

    def is_less_or_equal_to(self, other):
        """Assert that this is greater than other."""
        msg = "Expected {} to be less or equal to {}".format(self.value, other)
        assert_less_equal_than(self.value, other, msg)
        return self

    def has_attribute(self, name):
        """Assert that this has an attribute with the given name.
        
        Args:
            name (str): the name of the attribute
        """
        msg = "Expected {} to have an attribute named {}".format(self.value, name)
        try:
            hasattr(self.value, name)
        except AttributeError:
            raise AssertionError(msg)
        return self

    def has_attribute_with_value(self, name, value):
        """Assert that this has an attribute with the given name and
        an optional value.
        
        Args:
            name (str): the name of the attribute
            value (str): the value of the attribute
        """
        msg = "Expected {} to have an attribute named {} with value {}".format(self.value, name, value)
        try:
            hasattr(self.value, name)
        except AttributeError:
            raise AssertionError(msg)
        assert_equal(self.value.__getattribute__(name), value, msg = "Expected {} to have an attribute named {} with value {}".format(self.value, name, value))
        return self
    
    # Bool Assertions
    
    def is_true(self):
        """Assert that the value is True."""
        assert_true(self.value)

    def is_false(self):
        """Assert that the value is False."""
        assert_false(self.value)

    is_not_true = is_false
    is_not_false = is_true
    
    # Collection Assertions

    def contains(self, obj):
        """Assert that this contain the given object."""
        msg = "Expected {} to contain {}".format(self.value, obj)
        assert_contains(self.value, obj, msg)
        return self

    def not_contains(self, obj):
        """Assert that this DO NOT contain the given object.
        
        Args:
            obj (object): the object to check for in this value
        """
        msg = "Expected {} not to contain {}".format(self.value, obj)
        assert_not_contains(self.value, obj, msg)
        return self

    def contains_key(self, key: str):
        """Assert that this contains the given key.
        
        Args:
            key (str): the key to check for in this collection
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} to contain key {}".format(self.value, key)
        assert_contains(self.value, key, msg)
        return self

    def not_contains_key(self, key):
        """Assert that this DO NOT contains the given key.
        
        Args:
            key (str): the key to check that it does not exist in this collection
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} not to contain key {}".format(self.value, key)
        assert_not_contains(self.value, key, msg)
        return self

    def contains_key_with_value(self, key: str, value: Any):
        """Assert that this contains the given key and value.
        
        Args:
            key (str): the key to check for in this collection
            value (Any): the value to expect for the given key value
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} to contain key {}".format(self.value, key)
        assert_contains(self.value, key, msg)
        msg = "Expected {} to have value {} for key {}".format(self.value, value, key)
        assert_equal(self.value[key], value, msg)
        return self
    
    has_key_with_value = contains_key_with_value
    has_key_and_value = contains_key_with_value

    def has_same_elements_as(self, other):
        """Assert that this and the other collection has the same elements."""
        msg = "Expected {} and {} to contain the same elements".format(self.value, other)
        assert_equal(sorted(self.value), sorted(other), msg)
        return self
    
    # Callable assertions

    @property
    def when_called(self):
        """Assert if called without arguments."""
        if not callable(self.value):
            raise TypeError("object asserted is not callable")
        self.args = []
        self.kwargs = {}
        return self

    if_called = when_called

    def when_called_with(self, *args, **kwargs):
        """Assert if called with the given arguments."""
        if not callable(self.value):
            raise TypeError("object asserted is not callable")
        self.args = args
        self.kwargs = kwargs
        return self

    if_called_with = when_called_with

    def raises(self, err: type):
        """Assert if called that the given error is raised."""
        assert_raises(err, self.value, *self.args, **self.kwargs)

    def returns(self, expected):
        """Assert if called that the given result is returned."""
        actual = self.value(*self.args, **self.kwargs)
        msg = "Expected {} but {} was returned".format(expected, actual)
        assert_equal(actual, expected, msg)
    
    # HTTP Assertions
    
    def has_status_successful(self):
        """Assert that the response has a successful HTTP status code."""
        msg = "Expected successful HTTP status code but was {}".format(self.value.status_code)
        assert_less_than(self.value.status_code, 400, msg)
        return self
    
    def has_status_failed(self):
        """Assert that the response has a failed HTTP status code."""
        msg = "Expected failed HTTP status code but was {}".format(self.value.status_code)
        assert_greater_equal_than(self.value.status_code, 400, msg)
        return self

    def has_status_ok(self):
        """Assert that the response has HTTP status code 200 (OK)."""
        return self._has_status(200)

    def has_status_created(self):
        """Assert that the response has HTTP status code 201 (Created)."""
        return self._has_status(201)

    def has_status_no_content(self):
        """Assert that the response has HTTP status code 204 (No content)."""
        return self._has_status(204)

    def has_status_bad_request(self):
        """Assert that the response has HTTP status code 400 (Bad request)."""
        return self._has_status(400)

    def has_status_unauthorized(self):
        """Assert that the response has HTTP status code 401 (Unauthorized)."""
        return self._has_status(401)

    def has_status_forbidden(self):
        """Assert that the response has HTTP status code 403 (Forbidden)."""
        return self._has_status(403)

    def has_status_not_found(self):
        """Assert that the response has HTTP status code 404 (Not found)."""
        return self._has_status(404)

    def has_status_method_not_allowed(self):
        """Assert that the response has HTTP status code 405 (Method not allowed)."""
        return self._has_status(405)

    def has_status_precondition_failed(self):
        """Assert that the response has HTTP status code 412 (Precondition failed)."""
        return self._has_status(412)
    
    def _has_status(self, expected: int):
        msg = "Expected HTTP status {} but was {}".format(expected, self.value.status_code)
        try:
            hasattr(self.value, "status_code")
        except AttributeError:
            raise AssertionError("{} does not have any 'status_code' attribute")

        assert_equal(self.value.status_code, expected, msg)
        return self

    def body_equals(self, other_body: Union[dict, str]) -> object:
        """Assert that the response has a body equal to other_body.
        
        Args:
            other_body (Union[dict, str]): the body to compare to
        """
        if isinstance(other_body, dict):
            my_body = self.value.json()
        elif isinstance(other_body, str):
            my_body = self.value.text
        else:
            raise TypeError("cannot compare body with type {}".format(type(other_body)))

        print(my_body)
        msg = "Expected body {} to equal {}".format(my_body, other_body)
        assert_equal(my_body, other_body, msg)
        return self

    def body_length(self, length: int):
        """Assert that the response has a body has the given length.

        Args:
            length (int): the expected length of the body
        """
        actual = len(self.value.json())
        msg = "Expected body length to be {} but was {}".format(actual, length)
        assert_equal(actual, length, msg)
        return self

    def body_contains_key(self, key: str):
        """Assert that the response body contains the given key.

        Args:
            key (str): the key to check if it exists in the body
        """
        msg = "Expected body {} to contain key {}".format(self.value.json(), key)
        assert_contains(self.value.json(), key, msg)
        return self
