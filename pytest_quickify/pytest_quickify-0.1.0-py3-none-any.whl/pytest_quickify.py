"""Run test suites with pytest-quickify."""

__version__ = '0.1.0'


def pytest_addoption(parser):
    """Turn on quickify with --quick option"""
    group=parser.getgroup('quickify')
    group.addoption("--quick", action="store_true", help="quickify: Order your test suite")


def putest_report_header(config):
    """Thank tester for running test."""
    if config.getoption('quickify'):
        return "Thanks for running the tests."


def pytest_report_teststatus(report):
    """Order your test suite"""
    if report.when == 'call':
        if report.failed and pytest.config.getoption('quickify'):
            return (report.outcome, 'O', 'Order your test suite')