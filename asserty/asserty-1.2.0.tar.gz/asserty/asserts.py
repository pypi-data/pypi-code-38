from unittest import TestCase
from typing import Any, Union, Iterable

tc = TestCase("__init__")


def assert_true(obj, msg: str = ""):
    """Assert that obj evaluates to True."""
    tc.assertTrue(obj, msg)


def assert_false(obj, msg: str = ""):
    """Assert that obj evaluates to False."""
    tc.assertFalse(obj, msg)


def assert_none(obj, msg: str = ""):
    """Assert that obj is None."""
    tc.assertIsNone(obj, msg)


def assert_not_none(obj, msg: str = ""):
    """Assert that obj is NOT None."""
    tc.assertIsNotNone(obj, msg)


def assert_equal(obj1, obj2, msg: str = ""):
    """Assert that obj1 is equal to obj2."""
    tc.assertEqual(obj1, obj2, msg)


def assert_not_equal(obj1, obj2, msg: str = ""):
    """Assert that obj1 is NOT equal to obj2."""
    tc.assertNotEqual(obj1, obj2, msg)


def assert_greater_than(a, b, msg: str = ""):
    """Assert that a is greater than b."""
    tc.assertGreater(a, b, msg)


def assert_greater_equal_to(a, b, msg: str = ""):
    """Assert that a is greater or equal to b."""
    tc.assertGreaterEqual(a, b, msg)


def assert_less_than(a, b, msg: str = ""):
    """Assert that a is less than b."""
    tc.assertLess(a, b, msg)


def assert_less_equal_to(a, b, msg: str = ""):
    """Assert that a is less or equal to b."""
    tc.assertLessEqual(a, b, msg)


def assert_raises(err, func, *args, **kwargs):
    """Assert that if func is called with the given arguments it raises an error of the given type."""
    tc.assertRaises(err, func, *args, **kwargs)


def assert_type(obj: object, t: type, msg: str = ""):
    """Assert that obj is of the given type."""
    tc.assertIsInstance(obj, t, msg)


def assert_not_type(obj, t: type, msg: str = ""):
    """Assert that obj is NOT of the given type."""
    tc.assertNotIsInstance(obj, t, msg)


def assert_iterable(obj, msg: str = ""):
    """Assert that obj is an iterable type."""
    try:
        iter(obj)
    except TypeError:
        tc.fail(msg)


def fail(msg: str):
    """Fail with the given message."""
    tc.fail(msg)


def assert_contains(coll: Iterable, obj: object, msg=""):
    """Assert that coll contains the given object."""
    tc.assertIn(obj, coll, msg)


def assert_not_contains(coll, obj, msg=""):
    """Assert that coll NOT contains the given object."""
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
    and_that = also

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
        msg = "Expected {} to have type {} but was {}" \
            .format(self.value, type(self.value), expected)
        assert_type(self.value, expected, msg)
        return self

    has_same_type_as = has_type
    is_instance = has_type
    is_instance_type = has_type

    def not_has_type(self, expected):
        """Assert that this NOT have the expected type."""
        if not isinstance(expected, type):
            expected = type(expected)
        msg = "Expected {} not to have type {} but was".format(self.value, expected)
        assert_not_type(self.value, expected, msg)
        return self

    not_has_same_type_as = not_has_type
    not_is_instance = not_has_type
    not_is_instance_type = not_has_type

    def is_in(self, coll: Iterable):
        """Assert that this is in the given collection."""
        msg = "Expected {} to be in {} but was not".format(self.value, coll)
        assert_contains(coll, self.value, msg)
        return self

    def is_not_in(self, coll: Iterable):
        """Assert that this is NOT in the given collection."""
        msg = "Expected {} not to be in {} but was".format(self.value, coll)
        assert_not_contains(coll, self.value, msg)
        return self

    def has_length(self, expected):
        """Assert that this is of the expected length."""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length {} but was {}" \
            .format(self.value, expected, len(self.value))
        assert_equal(len(self.value), expected, msg)
        return self

    def not_has_length(self, expected):
        """Assert that this is NOT of the expected length."""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length {} but was".format(self.value, expected)
        assert_not_equal(len(self.value), expected, msg)
        return self

    def has_length_greater_than(self, expected: int):
        """Assert that the length is greater than the given value."""
        if hasattr(expected, "__len__"):
            expected = len(expected)

        msg = "Expected {} to have length greater than {} but was {}" \
            .format(self.value, expected, len(self.value))
        assert_greater_than(len(self.value), expected, msg)
        return self

    def has_length_greater_or_equal_to(self, expected):
        """Assert that the length is greater or equal to the given value."""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length greater or equal to {} but was {}" \
            .format(self.value, expected, len(self.value))
        assert_greater_equal_to(len(self.value), expected, msg)
        return self

    def has_length_less_than(self, expected):
        """Assert that the length is less than the given value."""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length less than {} but was".format(self.value, expected)
        assert_less_than(len(self.value), expected, msg)
        return self

    def has_length_less_or_equal_to(self, expected):
        """Assert that the length is less or equal to the given value."""
        if hasattr(expected, "__len__"):
            expected = len(expected)
        msg = "Expected {} to have length less or equal to {} but was".format(self.value, expected)
        assert_less_equal_to(len(self.value), expected, msg)
        return self

    def is_greater_than(self, other):
        """Assert that this is greater than other."""
        msg = "Expected {} to be greater than {}".format(self.value, other)
        assert_greater_than(self.value, other, msg)
        return self

    def is_greater_or_equal_to(self, other):
        """Assert that this is greater or equal to the other."""
        msg = "Expected {} to be greater or equal to {}".format(self.value, other)
        assert_greater_equal_to(self.value, other, msg)
        return self

    def is_less_than(self, other):
        """Assert that this is less than other."""
        msg = "Expected {} to be less than {}".format(self.value, other)
        assert_less_than(self.value, other, msg)
        return self

    def is_less_or_equal_to(self, other):
        """Assert that this is less or equal to the other."""
        msg = "Expected {} to be less or equal to {}".format(self.value, other)
        assert_less_equal_to(self.value, other, msg)
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
        msg = "Expected {} to have an attribute named {} with value {}" \
            .format(self.value, name, value)
        try:
            hasattr(self.value, name)
        except AttributeError:
            raise AssertionError(msg)
        assert_equal(self.value.__getattribute__(name), value,
                     msg="Expected {} to have an attribute named {} with value {}"
                     .format(self.value, name, value))
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

    def is_iterable(self):
        """Assert that this object is an iterable."""
        msg = "Expected {} to be an iterable".format(self.value)
        assert_iterable(self.value, msg)

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

    def contains_subset(self, subset: Iterable):
        """Assert that this contains the given sub-set.

        Args:
            subset (Iterable): the collection that is expected to exist in this
        """
        msg = "Expected {} to contain the subset {}".format(self.value, subset)
        self.is_iterable()
        assert_iterable(subset)

        if not isinstance(self.value, set):
            superset = set(self.value)
        else:
            superset = self.value

        if not isinstance(subset, set):
            subset = set(subset)

        if subset.issubset(superset):
            return self
        else:
            fail(msg)

    has_subset = contains_subset

    def is_subset_of(self, superset: Iterable):
        """Assert that this is a sub-set of the given super-set.

        Args:
            superset (Iterable): the collection that is expected to be a super-set of this
        """
        msg = "Expected {} to contain the sub-set {}".format(superset, self.value)
        self.is_iterable()
        assert_iterable(superset)

        if not isinstance(self.value, set):
            subset = set(self.value)
        else:
            subset = self.value

        if not isinstance(superset, set):
            superset = set(superset)

        if subset.issubset(superset):
            return self
        else:
            fail(msg)

    def has_same_elements_as(self, other: Iterable):
        """Assert that this and the other collection has the same elements."""
        msg = "Expected {} and {} to contain the same elements".format(self.value, other)
        self.is_iterable()
        assert_iterable(other)
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
        assert_greater_equal_to(self.value.status_code, 400, msg)
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

    def body_length(self, length: int):
        """Assert that the response body has the given length. 

        Args:
            length (int): the expected length of the body
        """
        msg = "Expected body {} to have length {}".format(self.value.json(), length)
        assert_equal(len(self.value.json()), length, msg)
        return self

    def body_equals(self, obj: Union[dict, str]):
        """Assert that the response has a body equal to other_body.

        Args:
            obj (Union[dict, str]): the body to compare to
        """
        if isinstance(obj, dict):
            my_body = self.value.json()
        elif isinstance(obj, str):
            my_body = self.value.text
        else:
            raise TypeError("cannot compare body with type {}".format(type(obj)))

        msg = "Expected body {} to equal {}".format(my_body, obj)
        assert_equal(my_body, obj, msg)
        return self

    def body_contains_key(self, key: str):
        """Assert that the response body contains the given key.

        Args:
            key (str): the key to check if it exists in the body
        """
        msg = "Expected body {} to contain key {}".format(self.value.json(), key)
        assert_contains(self.value.json(), key, msg)
        return self

    def body_contains_key_with_value(self, key: str, value: Any):
        """Assert that the response body contains the given key and value.

        Args:
            key (str): the key to check if it exists in the body
            value (Any): the value that is expected
        """
        msg = "Expected body {} to contain key {} with value {}" \
            .format(self.value.json(), key, value)
        assert_contains(self.value.json(), key, msg)
        assert_equal(self.value.json()[key], value, msg)
        return self

    def body_contains_subset(self, subset: Iterable):
        """Assert that the response body contains the given sub-set.

        Args:
            subset (Iterable): the sub-set which is expected in this body
        """
        msg = "Expected body {} to contain sub-set {}".format(self.value.json(), subset)
        assert_iterable(subset)

        if not isinstance(subset, set):
            subset = set(subset)

        if subset.issubset(self.value.json()):
            return self
        else:
            fail(msg)
