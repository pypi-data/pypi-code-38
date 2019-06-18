"""A collection of assertions."""


def assert_not_none(item):
    """Assert that the given item is not None."""
    assert item is not None, 'Item given is None.'


def assert_type(item, *item_types):
    """Assert the given item is a particular type."""
    assert isinstance(item, item_types), 'Item type {0} not in types: {1}'.format(type(item), item_types)
