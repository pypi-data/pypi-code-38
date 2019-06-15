import re
import pytest
import functools
from pathlib import Path
from click.testing import CliRunner


def pytest_addoption(parser):
    parser.addoption(
        "--tt",
        "--test-fixture",
        action="store_true",
        default=False,
        help="Tests fixture functions."
    )
    parser.addoption(
        "--dd",
        "--display",
        action="store_true",
        default=False,
        help="Test with image display."
    )


def pytest_collection_modifyitems(config, items):
    def skip_by_mark(option, mark):
        if config.getoption(option):
            # <option> given in cli:
            # skip all functions not marked with <mark>
            for item in items:
                if mark not in item.keywords:
                    item.add_marker(pytest.mark.skip(reason=f"not marked with {option}: {item.name}"))
        else:
            # <option> not given in cli:
            # skip all functions marked with <mark>
            for item in items:
                if mark in item.keywords:
                    item.add_marker(pytest.mark.skip(reason=f"marked with {option}: {item.name}"))

    def run_marked_first(mark):
        _marked = []
        _unmarked = []

        for item in items:
            if mark in item.keywords:
                _marked.append(item)
            else:
                _unmarked.append(item)

        items[:] = [*_marked, *_unmarked]

    run_marked_first('critic')
    skip_by_mark('--tt', 'test_fixture')
    skip_by_mark('--dd', 'display')


@pytest.fixture(scope="session")
def cli_invoker():
    return functools.partial(CliRunner().invoke, catch_exceptions=False)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    # setattr(item, "rep_" + rep.when, rep)
    setattr(item, "report", rep)


import pprint


@pytest.fixture
def critical_fail(request):
    """Skip all functions in this module if a function with @pytest.mark.critic fails.
    """
    yield

    # if hasattr(request.node, 'rep_call'):
    #     report = request.node.rep_call.failed
    # elif hasattr(request.node, 'rep_setup'):
    #     report = request.node.rep_setup.failed
    report = request.node.report.failed

    if report and request.node.get_closest_marker('critic'):
        module_name = request.node._location[0]

        for item in request.session.items:
            item_name = item.name.split('[')[0]

            if item.parent.name == module_name and \
                    hasattr(request.module, item_name) and \
                    not item.get_closest_marker('skip'):

                item.add_marker(pytest.mark.skip(reason=f"Critical test '{request.node.name}' failed."))


@pytest.fixture(scope="module")
def file_contents(request):
    def _file_contents(key=None, file=''):
        _input = Path(file)
        _dict = dict()

        if not _input.is_file():
            _input = Path(__file__).parent / file
            if not _input.is_file():
                pytest.skip(f"invalid file path '{file}'")

        for item in _input.read_text().split('"""\n\n'):
            k, v = item.split(' = """\\\n')
            _dict[k] = re.sub('"""\n*$', '', v)

        return _dict[key] if key else _dict

    return _file_contents


@pytest.fixture(scope="module")
def make_file():
    def _make_file(name, tempdir, contents=''):
        file = tempdir / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(contents)

        return file

    return _make_file


@pytest.fixture
def getfixture(request):
    def _getfixture(name):
        return request.getfixturevalue(name)
    return _getfixture
