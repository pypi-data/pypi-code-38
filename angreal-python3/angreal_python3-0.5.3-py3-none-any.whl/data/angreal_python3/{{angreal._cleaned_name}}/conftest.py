def pytest_itemcollected(item):
    """
    use test doc strings as messages for the testing suite
    :param item:
    :return:
    """
    if item._obj.__doc__:
        item._nodeid = item.obj.__doc__.strip()
