# content of conftest.py


def pytest_addoption(parser):
    parser.addoption("--integration", action="store_true", help="run integration tests")
