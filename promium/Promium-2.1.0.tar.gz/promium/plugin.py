import os
import datetime
import logging
import pytest

from selenium.common.exceptions import (
    WebDriverException,
    ElementNotVisibleException,
    InvalidElementStateException,
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException
)

from promium.logger import Logger
from promium.exceptions import BrowserConsoleException

log = logging.getLogger(__name__)


def pytest_sessionstart(session):
    if hasattr(session.config, 'cache'):
        cache = session.config.cache
        cache_path = "cache/{}".format(session.config.lastfailed_file)
        print("Lastfailed:", len(cache.get(cache_path, set())))
    session.run_duration = datetime.datetime.now()
    print("\nPytest session start %s\n" % session.run_duration)


@pytest.mark.trylast
def pytest_sessionfinish(session):
    finish = datetime.datetime.now()
    duration = datetime.timedelta(
        seconds=(finish - session.run_duration).seconds
    )
    print("\n\nPytest session finish %s (duration=%s)\n" % (finish, duration))


@pytest.hookimpl
def pytest_addoption(parser):
    parser.addoption(
        "--capturelog",
        dest="logger",
        default=None,
        action="store_true",
        help="Show log messages for each failed test"
    )
    parser.addoption(
        "--fail-debug-info",
        action="store_true",
        help="Show screenshot and test case urls for each failed test"
    )
    parser.addoption(
        "--duration-time",
        action="store_true",
        help="Show the very slow test"
    )
    parser.addoption(
        "--highlight",
        action="store_true",
        help="Highlighting elements"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="Enable headless mode for Chrome browser only"
    )
    parser.addoption(
        "--chrome",
        action="store_true",
        help="Use chrome browser"
    )
    parser.addoption(
        "--firefox",
        action="store_true",
        help="Use firefox browser"
    )
    parser.addoption(
        "--opera",
        action="store_true",
        help="Use opera browser"
    )
    parser.addoption(
        "--repeat",
        action="store",
        default=1,
        type="int",
        metavar='repeat',
        help='Number of times to repeat each test. Mostly for debug purposes'
    )
    parser.addoption(
        "--check-console",
        action="store_true",
        help="Check browser console js and other errors"
    )
    parser.addoption(
        "-U",
        "--disable-test-case-url",
        action="store_false",
        help="If the flag is on, it turns off the mandatory test case"
    )


def pytest_generate_tests(metafunc):
    if metafunc.config.option.repeat > 1:
        metafunc.fixturenames.append('repeat')
        metafunc.parametrize('repeat', range(metafunc.config.option.repeat))


@pytest.fixture(autouse=True)
def logger(request):
    return logging.getLogger()


@pytest.mark.trylast
def pytest_runtest_call(item):
    if hasattr(item.config, "assertion_errors"):
        if item.config.assertion_errors:
            msg = "\n{assertion_errors_list}\n".format(
                assertion_errors_list="\n".join(item.config.assertion_errors)
            )
            raise AssertionError(msg)
    if item.config.getoption("--check-console"):
        if hasattr(item.config, "check_console_errors"):
            browser_console_errors = item.config.check_console_errors()
            if browser_console_errors:
                msg = (
                    "Browser console js errors found:"
                    "\n{console_errors}\n".format(
                        console_errors=u"\n".join(
                            browser_console_errors
                        )
                    )
                )
                raise BrowserConsoleException(msg)


@pytest.mark.tryfirst
@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """pytest failed test report generator"""
    html_plugin = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    when = report.when
    excinfo = call.excinfo
    extra = getattr(report, 'extra', [])
    if excinfo:
        if excinfo.type in [
            ElementNotVisibleException,
            InvalidElementStateException,
            InvalidSelectorException,
            NoSuchElementException,
            StaleElementReferenceException
        ] and report.longrepr:
            report.longrepr.reprtraceback.reprentries[-1].lines = \
                report.longrepr.reprtraceback.reprentries[-1].lines[:2]
    
    if when == "call" and not report.passed:
        if item.config.getoption("--fail-debug-info"):
            fail_info = "Fail info not found."
            try:
                if hasattr(item.config, "get_fail_debug"):
                    fail_debug = item.config.get_fail_debug()
                    for k in (dict(os.environ)).keys():
                        if 'VAGGA' in k:
                            break
                    if fail_debug.test_type == 'selenium':
                        fail_info = (
                            (
                                "\nURL: {url}"
                                "\nTEST CASE: {test_case}"
                                "\nSCREENSHOT: {screenshot}"
                                "\nRUN_COMMAND: {run_command}"
                                "\nTXID: {txid}"
                            
                            ).format(
                                url=fail_debug.url,
                                screenshot=fail_debug.screenshot,
                                test_case=fail_debug.test_case,
                                run_command=fail_debug.run_command,
                                txid=fail_debug.txid
                            )
                        )
                        extra.append(html_plugin.extras.url(
                            fail_debug.screenshot, name="SCREENSHOT"
                        ))
                        extra.append(
                            html_plugin.extras.html(
                                "<img src=\"{img}\" "
                                "height=\"230\" width=\"auto\" align=\""
                                "right\" bottom=\"0px\">Screenshot</img>"
                                    .format(
                                    img=fail_debug.screenshot
                                )
                            )
                        )
                    
                    elif fail_debug.test_type == 'request':
                        fail_info = (
                            "\nURL: {url}"
                            "\nTEST_CASE: {test_case}"
                            "\nSTATUS_CODE: {status_code}"
                            "\nRUN_COMMAND: {run_command}"
                            "\nTXID: {txid}"
                        ).format(
                            url=fail_debug.url,
                            test_case=fail_debug.test_case,
                            status_code=fail_debug.status_code,
                            run_command=fail_debug.run_command,
                            txid=fail_debug.txid
                        )
                    extra.append(html_plugin.extras.url(
                        fail_debug.url, name="URL"
                    ))
                    extra.append(html_plugin.extras.url(
                        fail_debug.test_case, name="TEST_CASE"
                    ))
                    report.extra = extra
            
            except WebDriverException as e:
                fail_info = (
                    "\nWebdriver instance must have crushed: {msg}".format(
                        msg=e.msg
                    )
                )
            finally:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    longrepr.sections.insert(
                        0, ("Captured stdout %s" % when, fail_info, "-")
                    )
        
        if item.config.getoption("--duration-time"):
            duration = call.stop - call.start
            if duration > 120:
                report.sections.append((
                    "Captured stdout %s" % when,
                    ("\n\n!!!!! The very slow test. "
                     "Duration time is %s !!!!!\n\n")
                    % datetime.datetime.fromtimestamp(duration).strftime(
                        "%M min %S sec"
                    )
                ))


def pytest_configure(config):
    os.environ['PYTHONWARNINGS'] = (
        'ignore:An HTTPS request has been made, '
        'ignore:A true SSLContext object is not available, '
        'ignore:Unverified HTTPS request is being made'
    )
    os.environ['TEST_CASE'] = "False"
    
    if config.getoption('--headless'):
        os.environ['HEADLESS'] = 'Enabled'
    if config.getoption("--highlight"):
        os.environ['HIGHLIGHT'] = 'Enabled'
    if config.getoption("--capturelog"):
        config.pluginmanager.register(Logger(), "logger")
    if config.getoption("--check-console"):
        os.environ['CHECK_CONSOLE'] = 'Enabled'
    if not getattr(config, "lastfailed_file", None):
        config.lastfailed_file = "lastfailed"
    if config.getoption("--disable-test-case-url"):
        os.environ['TEST_CASE'] = "True"
