from .plugin import PyTestBug


def pytest_configure(config):
    config.addinivalue_line("markers", "bug(*args, run: bool): Mark test as a bug")
    config.pluginmanager.register(PyTestBug(config), name="pytest-bug-instance")
