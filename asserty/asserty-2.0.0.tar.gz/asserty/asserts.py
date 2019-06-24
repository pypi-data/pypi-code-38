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


def is_subset(super_container, sub_container):
    """Used to assert subsets recursively."""
    t1 = type(super_container)
    t2 = type(sub_container)
    assert t1 == t2

    types = t1
    if types == dict:
        # Check that all keys of sub_container is in super_container
        super_keys_set = set(super_container.keys())
        sub_keys_set = set(sub_container.keys())
        assert sub_keys_set.issubset(super_keys_set)
        # Assert the values
        for key in sub_keys_set:
            is_subset(super_container[key], sub_container[key])
    elif types == list or types == set:
        assert len(sub_container) <= len(super_container)
        super_sorted = sorted(super_container)
        sub_sorted = sorted(sub_container)
        for i in range(len(sub_sorted)):
            is_subset(super_sorted[i], sub_sorted[i])
    else:
        assert super_container == sub_container


class Assert:
    def __init__(self, value):
        self.value = value

    def is_none(self):
        """Assert that this has a value of None.
        
        Examples:
            >>> from asserty import assert_that
            >>> def echo(arg): return arg
            >>> assert_that(echo(None)).is_none()
        """
        msg = "Expected {} to be None".format(self.value)
        assert_none(self.value, msg)

    def is_not_none(self):
        """Assert that this DO NOT has a value of None.
        
        Examples:
            >>> from asserty import assert_that, version
            >>> assert_that(version).is_not_none()
        """
        msg = "Expected {} to be None".format(self.value)
        assert_not_none(self.value, msg)

    def equals(self, other: object):
        """Assert that if this object is equal to the other object.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that("HELLO".lower()).equals("hello")
        """
        msg = "Expected {} to equal".format(self.value, other)
        assert_equal(self.value, other, msg)

    def not_equals(self, other: object):
        """Check that if this object DO NOT equal to the other object.
        
        Args:
            other (object): the other object which this value is expected NOT to equal.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that("HELLO").not_equals("hello")
        """
        msg = "Expected {} not to equal".format(self.value, other)
        assert_not_equal(self.value, other, msg)

    def has_type(self, expected: Union[type, object]):
        """Assert that this has the expected type.
        
        Args:
            expected (type, object): the expected type of this value. If expected is
                not a type, type(expected) will be used.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that("str").has_type(str)
            >>> assert_that("str").has_type("string")
        """
        if not isinstance(expected, type):
            expected = type(expected)
        msg = "Expected {} to have type {} but was {}" \
            .format(self.value, type(self.value), expected)
        assert_type(self.value, expected, msg)

    has_same_type_as = has_type
    is_instance = has_type
    is_instance_type = has_type

    def not_has_type(self, expected: type):
        """Assert that this NOT have the expected type.
        
        Args:
            expected (type, object): the type to not exppect of this value. If expected is
                not a type, type(expected) will be used.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that("str").not_has_type(int)
            >>> assert_that("str").not_has_type(1)
        """
        if not isinstance(expected, type):
            expected = type(expected)
        msg = "Expected {} not to have type {} but was".format(self.value, expected)
        assert_not_type(self.value, expected, msg)

    not_has_same_type_as = not_has_type
    not_is_instance = not_has_type
    not_is_instance_type = not_has_type

    def is_in(self, coll: Iterable):
        """Assert that this is in the given collection.
        
        Args:
            coll (Iterable): the collection which this value is expected to be found in.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that(1).is_in([1,2,3]) # list
            >>> assert_that("key").is_in({"key": "value"}) # dict
            >>> assert_that("a").is_in("asserty") # string
        """
        msg = "Expected {} to be in {} but was not".format(self.value, coll)
        assert_contains(coll, self.value, msg)

    def is_not_in(self, coll: Iterable):
        """Assert that this is NOT in the given collection.
        
        Args:
            coll (Iterable): the collection which this value is NOT expected to be in.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that(-1).is_not_in([1,2,3]) # list
            >>> assert_that("keys").is_not_in({"key": "value"}) # dict
            >>> assert_that("EEE").is_not_in("asserty") # string
        """
        msg = "Expected {} not to be in {} but was".format(self.value, coll)
        assert_not_contains(coll, self.value, msg)

    def has_length(self, expected: int):
        """Assert that this is of the expected length.
        
        Args:
            expected (int): the expected length of this value.
        
        Raises:
            TypeError: if expected is not an int or misses __len__ attribute.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([]).has_length(0)
            >>> assert_that("str").has_length(3)
            >>> assert_that([1,2,3]).has_length([4,5,6]) # Also works with other collections lengths
        """
        msg = f"Expected {self.value} to have length {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_equal, msg)

    def not_has_length(self, expected: int):
        """Assert that this is NOT of the expected length.
        
        Args:
            expected (int): the length that this value is not expected to have.
        
        Raises:
            TypeError: if expected is not an int or misses __len__ attribute.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([]).not_has_length(1)
            >>> assert_that([1,2,3]).not_has_length([4,5])
            >>> assert_that("str").not_has_length(4)
        """
        msg = f"Expected {self.value} to have length {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_not_equal, msg)

    def has_length_greater_than(self, expected: Union[int, Iterable]):
        """Assert that the length is greater than the given value.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).has_length_greater_than(2)
        """
        msg = f"Expected {self.value} to have length greater than {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_greater_than, msg)

    def has_length_greater_or_equal_to(self, expected: Union[int, Iterable]):
        """Assert that the length is greater or equal to the given value.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).has_length_greater_or_equal_to(3)
        """
        msg = f"Expected {self.value} to have length greater or equal to {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_greater_equal_to, msg)

    def has_length_less_than(self, expected: Union[int, Iterable]):
        """Assert that the length is less than the given value.
        
         Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).has_length_less_than(5)
        """
        msg = f"Expected {self.value} to have length less than {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_less_than, msg)

    def has_length_less_or_equal_to(self, expected: Union[int, Iterable]):
        """Assert that the length is less or equal to the given value.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).has_length_less_or_equal_to(3)
        """
        msg = f"Expected {self.value} to have length less or equal to {expected} but was {len(self.value)}"
        self._assert_length(expected, assert_less_equal_to, msg)
    
    def _assert_length(self, expected: Union[int, Iterable], operator: callable, msg):
        if isinstance(expected, int):
            pass
        elif hasattr(expected, "__len__"):
            expected = len(expected)
        else:
            raise TypeError("expected value isn't an integer or is missing __len__ attribute")
        
        self.has_attribute("__len__")
        operator(len(self.value), expected, msg)

    def is_greater_than(self, other):
        """Assert that this is greater than other.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that(10).is_greater_than(9)
        """
        msg = "Expected {} to be greater than {}".format(self.value, other)
        assert_greater_than(self.value, other, msg)

    def is_greater_or_equal_to(self, other):
        """Assert that this is greater or equal to the other.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that(10).is_greater_or_equal_to(9)
        """
        msg = "Expected {} to be greater or equal to {}".format(self.value, other)
        assert_greater_equal_to(self.value, other, msg)

    def is_less_than(self, other):
        """Assert that this is less than other.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that(10).is_less_than(12)
        """
        msg = "Expected {} to be less than {}".format(self.value, other)
        assert_less_than(self.value, other, msg)

    def is_less_or_equal_to(self, other):
        """Assert that this is less or equal to the other.

        Examples:
            >>> from asserty import assert_that
            >>> assert_that(10).is_less_or_equal_to(11)
        """
        msg = "Expected {} to be less or equal to {}".format(self.value, other)
        assert_less_equal_to(self.value, other, msg)

    def has_attribute(self, name: str):
        """Assert that this has an attribute with the given name.

        Args:
            name (str): the name of the attribute
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).has_attribute("__len__")
        """
        msg = "Expected {} to have an attribute named {}".format(self.value, name)
        try:
            hasattr(self.value, name)
        except AttributeError:
            raise AssertionError(msg)

    def has_attribute_with_value(self, name, value: object):
        """Assert that this has an attribute with the given name and value.

        Args:
            name (str): the name of the attribute
            value (object): the value of the attribute
        
        Examples:
            >>> from asserty import assert_that
            >>> class X: pos = (1, 2)
            >>> assert_that(X()).has_attribute_with_value("pos", (1, 2))
        """
        msg = f"Expected {self.value} to have an attribute named {name} with value {value}"
        try:
            hasattr(self.value, name)
        except AttributeError:
            raise AssertionError(msg)
        assert_equal(self.value.__getattribute__(name), value, msg)

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
        """Assert that this object is an iterable.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).is_iterable()
            >>> assert_that(1).is_iterable()
            Traceback (most recent call last):
            ...
            AssertionError: Expected 1 to be an iterable
        """
        msg = "Expected {} to be an iterable".format(self.value)
        assert_iterable(self.value, msg)

    def contains(self, obj):
        """Assert that this contain the given object.
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).contains(1)
            >>> assert_that("Cookies").contains("ok")
            >>> assert_that({"a": 1}).contains("a")
        """
        msg = "Expected {} to contain {}".format(self.value, obj)
        assert_contains(self.value, obj, msg)

    def not_contains(self, obj):
        """Assert that this DO NOT contain the given object.

        Args:
            obj (object): the object to check for in this value
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that([1, 2, 3]).not_contains(4)
            >>> assert_that("Cookies").not_contains("sky")
            >>> assert_that({}).not_contains("sky")
        """
        msg = "Expected {} not to contain {}".format(self.value, obj)
        assert_not_contains(self.value, obj, msg)

    def contains_key(self, key: str):
        """Assert that this contains the given key.

        Args:
            key (str): the key to check for in this dictionary
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that({"a": 1}).contains_key("a")
            >>> assert_that({}).contains_key("a")
            Traceback (most recent call last):
            ...
            AssertionError: 'a' not found in {} : Expected {} to contain key a
            
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} to contain key {}".format(self.value, key)
        assert_contains(self.value, key, msg)

    def not_contains_key(self, key):
        """Assert that this DO NOT contains the given key.

        Args:
            key (str): the key to check that it does not exist in this collection
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that({"a": 1}).not_contains_key("b")
            >>> assert_that({}).not_contains_key("a")
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} not to contain key {}".format(self.value, key)
        assert_not_contains(self.value, key, msg)

    def contains_key_with_value(self, key: str, value: object):
        """Assert that this contains the given key and value.

        Args:
            key (str): the key to check for in this collection
            value (Any): the value to expect for the given key value
        
        Examples:
            >>> from asserty import assert_that
            >>> assert_that({"a": 1}).contains_key_with_value("a", 1)
        """
        if not hasattr(self.value, "__contains__"):
            raise TypeError("value has no keys")
        msg = "Expected {} to contain key {}".format(self.value, key)
        assert_contains(self.value, key, msg)
        msg = "Expected {} to have value {} for key {}".format(self.value, value, key)
        assert_equal(self.value[key], value, msg)

    has_key_with_value = contains_key_with_value
    has_key_and_value = contains_key_with_value

    def contains_subset(self, subset: Union[dict, list, set], **kwargs):
        """Assert that this contains the given sub-set.
        
        This can be used on dict, list and set types and works recursively (if used correctly).
        It can be used to assert that, for instance, a dict is contained in another dict in the sense
        that the super-set has all the keys of the subs-set at the correct structure as well as the
        values for the matching keys. See examples for a demo how it works.

        Args:
            subset (Union[dict, list, set]): the collection that is expected to exist in this
            **kwargs:
                recursive (bool): whether to check the subset recursively
        
        Example:
            >>> from asserty import assert_that
            >>> assert_that({1, 2, 3}).contains_subset({1}) # Regular sets
            >>> assert_that([1, 2, 3]).contains_subset([1, 2]) # Works with lists as well
            >>> superset = {"a": 1, "b": {"c": 2}} # Lets test recursive
            >>> subset = {"b": {"c": 2}}           # A sub-set of the dict defined above
            >>> assert_that(superset).contains_subset(subset, recursive=True)
            >>> subset = {"b": {"c": 3}}           # Change value
            >>> assert_that(superset).contains_subset(subset, recursive=True)
            Traceback (most recent call last):
            ...
            AssertionError: Expected {'a': 1, 'b': {'c': 2}} to contain the sub-set {'b': {'c': 3}}
        """
        self._assert_subset(self.value, subset, **kwargs)

    has_subset = contains_subset

    def is_subset_of(self, superset: Union[dict, list, set], **kwargs):
        """Assert that this is a sub-set of the given super-set.

        Args:
            superset (set): the collection that is expected to be a super-set of this
        
        Example:
            >>> from asserty import assert_that
            >>> assert_that({1}).is_subset_of({1, 2, 3}) # Regular sets
            >>> assert_that([2]).is_subset_of([1, 2, 3]) # Works with lists as well
            >>> superset = {"a": 1, "b": {"c": 2}} # Lets test recursive
            >>> subset = {"b": {"c": 2}}           # A sub-set of the dict defined above
            >>> assert_that(subset).is_subset_of(superset, recursive=True)
            >>> subset = {"b": {"c": 3}}           # Change value
            >>> assert_that(subset).is_subset_of(superset, recursive=True)
            Traceback (most recent call last):
            ...
            AssertionError: Expected {'a': 1, 'b': {'c': 2}} to contain the sub-set {'b': {'c': 3}}
        """
        self._assert_subset(superset, self.value, **kwargs)

    @staticmethod
    def _assert_subset(superset: Union[dict, list, set], subset: Union[dict, list, set], **kwargs):
        msg = f"Expected {superset} to contain the sub-set {subset}"
        assert_iterable(superset)
        assert_iterable(subset)

        if "recursive" in kwargs and kwargs["recursive"]:
            try:
                is_subset(superset, subset)
            except AssertionError:
                raise AssertionError(msg)
        else:  # Do not assert complex structures recursively.
            if not isinstance(superset, set):
                superset = set(superset)

            if not isinstance(subset, set):
                subset = set(subset)

            assert subset.issubset(superset), msg

    def has_same_elements_as(self, other: Iterable):
        """Assert that this and the other collection has the same elements.
        
        Args:
            other (Iterable): other iterable to check the elements against
        
        Example:
            >>> from asserty import assert_that
            >>> assert_that([1, 3, 2, 4]).has_same_elements_as([1, 2, 3, 4])
            >>> assert_that([1, 2, 3, 4]).has_same_elements_as({4, 3, 2, 1}) # list and set
            >>> assert_that("trs").has_same_elements_as("str") # string
        """
        msg = "Expected {} and {} to contain the same elements".format(self.value, other)
        self.is_iterable()
        assert_iterable(other)
        assert_equal(sorted(self.value), sorted(other), msg)

    # Callable assertions

    @property
    def when_called(self):
        """Assert if called without arguments.
        
        Examples:
            >>> from asserty import assert_that
            >>> def fun(): return "Fun"
            >>> assert_that(fun).when_called.returns("Fun")
            >>> assert_that("str").when_called.returns("str")
            Traceback (most recent call last):
            ...
            TypeError: object asserted is not callable
        """
        if not callable(self.value):
            raise TypeError("object asserted is not callable")
        self.args = []
        self.kwargs = {}
        return self

    if_called = when_called

    def when_called_with(self, *args, **kwargs):
        """Assert if called with the given arguments. Used with 'returns' or 'raises'.
        
        Examples:
            >>> from asserty import assert_that
            >>> def pow(x: int): return x*x
            >>> assert_that(pow).when_called_with(5).returns(25)
            >>> assert_that("str").when_called_with(5).returns(25)
            Traceback (most recent call last):
            ...
            TypeError: object asserted is not callable
        """
        if not callable(self.value):
            raise TypeError("object asserted is not callable")
        self.args = args
        self.kwargs = kwargs
        return self

    if_called_with = when_called_with

    def raises(self, err: type):
        """Assert if called that the given error is raised.
        
        Examples:
            >>> from asserty import assert_that
            >>> def doom(x: int): return x / 0
            >>> assert_that(doom).when_called_with(5).raises(ZeroDivisionError)
        """
        assert_raises(err, self.value, *self.args, **self.kwargs)

    def returns(self, expected):
        """Assert if called that the given result is returned.
        
        Examples:
            >>> from asserty import assert_that
            >>> def pow(x: int): return x*x
            >>> assert_that(pow).when_called_with(5).returns(25)
        """
        actual = self.value(*self.args, **self.kwargs)
        msg = "Expected {} but {} was returned".format(expected, actual)
        assert_equal(actual, expected, msg)

    # HTTP Assertions

    def has_status_successful(self):
        """Assert that the response has a successful HTTP status code.
        
        Examples:
            >>> from asserty import assert_that
            >>> import requests
            >>> res = requests.get("https://google.com")
            >>> assert_that(res).has_status_successful()
        """
        msg = "Expected successful HTTP status code but was {}".format(self.value.status_code)
        assert_less_than(self.value.status_code, 400, msg)

    def has_status_failed(self):
        """Assert that the response has a failed HTTP status code.
        
        Examples:
            >>> from asserty import assert_that
            >>> import requests
            >>> res = requests.delete("https://google.com")
            >>> assert_that(res).has_status_failed()
        """
        msg = "Expected failed HTTP status code but was {}".format(self.value.status_code)
        assert_greater_equal_to(self.value.status_code, 400, msg)

    def has_status_ok(self):
        """Assert that the response has HTTP status code 200 (OK).
        
        Examples:
            >>> from asserty import assert_that
            >>> import requests
            >>> res = requests.get("https://google.com")
            >>> assert_that(res).has_status_ok()
        """
        return self._has_status(200)

    def has_status_created(self):
        """Assert that the response has HTTP status code 201 (Created)."""
        return self._has_status(201)

    def has_status_accepted(self):
        """Assert that the response has HTTP status code 202 (Accepted)."""
        return self._has_status(202)

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

    def has_status_conflict(self):
        """Assert that the response has HTTP status code 409 (Conflict)."""
        return self._has_status(409)

    def has_status_precondition_failed(self):
        """Assert that the response has HTTP status code 412 (Precondition failed)."""
        return self._has_status(412)

    def has_status_internal_server_error(self):
        """Assert that the response has HTTP status code 412 (Internal server error)."""
        return self._has_status(500)

    def has_status_service_unavailable(self):
        """Assert that the response has HTTP status code 503 (Service unavailable)."""
        return self._has_status(503)

    def has_status_gateway_timeout(self):
        """Assert that the response has HTTP status code 504 (Gateway timeout)."""
        return self._has_status(504)

    def _has_status(self, expected: int):
        for attr in ["status_code", "status", "statuscode"]:
            status = getattr(self.value, attr, 0)
            if status !=0:
                break

        if status == 0:
            raise TypeError("{} does not have any status code attribute")
        
        msg = "Expected HTTP status {} but was {}".format(expected, self.value.status_code)

        assert_equal(status, expected, msg)

    def body_length(self, length: int):
        """Assert that the response body has the given length. 

        Args:
            length (int): the expected length of the body
        """
        msg = "Expected body {} to have length {}".format(self.value.json(), length)
        assert_equal(len(self.value.json()), length, msg)

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

        msg = f"Expected body {my_body} to equal {obj}"
        assert_equal(my_body, obj, msg)

    def body_contains_key(self, key: str):
        """Assert that the response body contains the given key.

        Args:
            key (str): the key to check if it exists in the body
        """
        msg = "Expected body {} to contain key {}".format(self.value.json(), key)
        assert_contains(self.value.json(), key, msg)

    def body_contains_key_with_value(self, key: str, value: Any):
        """Assert that the response body contains the given key and value.

        Args:
            key (str): the key to check if it exists in the body
            value (Any): the value that is expected
        """
        msg = f"Expected body {self.value.json()} to contain key {key} with value {value}"
        assert_contains(self.value.json(), key, msg)
        assert_equal(self.value.json()[key], value, msg)

    def body_contains_subset(self, subset: dict):
        """Assert that the response body contains the given dict as a sub-set.

        Args:
            key (dict): a dict that is expected as a structure within this body
        """
        body = self.value.json()
        msg = f"Expected body {body} to contain sub-set {subset}"
        self._assert_subset(body, subset, recursive=True)
