import enum

import pytest
from . import hooks

__version__ = '0.2.2'

BUG = '_mark_bug'
COMMENT = '_bug_comment'


class MARKS(enum.Enum):
    SKIP = 'b'
    FAIL = 'f'
    PASS = 'p'
    UNKNOWN = 'u'


def bug_mark(*args, run=False, **kwargs):
    com = [str(i) for i in args]
    com.extend('%s=%s' % (key, value) for key, value in kwargs.items())
    return ', '.join(com) if com else 'no comment', run


class PyTestBug:

    def __init__(self, config):
        self.config = config
        self._skipped = 0
        self._failed = 0
        self._passed = 0

    def counter(self, mark):
        if mark is MARKS.SKIP:
            self._skipped += 1
        elif mark is MARKS.FAIL:
            self._failed += 1
        elif mark is MARKS.PASS:
            self._passed += 1

    @staticmethod
    def set_mark(obj, mark=MARKS.UNKNOWN):
        setattr(obj, BUG, mark)

    @staticmethod
    def set_comment(obj, comment):
        setattr(obj, COMMENT, 'BUG: %s' % str(comment))

    @staticmethod
    def pytest_addhooks(pluginmanager):
        pluginmanager.add_hookspecs(hooks)

    def pytest_runtest_setup(self, item):
        for i in item.iter_markers(name='bug'):
            comment, run = bug_mark(*i.args, **i.kwargs)
            self.set_comment(item, comment)
            if run:
                self.config.hook.pytest_bug_run_before_set_mark(item=item, config=self.config)
                self.set_mark(item)
                self.config.hook.pytest_bug_run_after_set_mark(item=item, config=self.config)
            else:
                self.set_mark(item, MARKS.SKIP)
                pytest.skip(comment)

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item):
        outcome = yield
        report = outcome.get_result()
        mark = getattr(item, BUG, None)
        if mark:
            self.set_comment(report, getattr(item, COMMENT))
            if report.skipped:
                self.set_mark(report, MARKS.SKIP)
            if report.when == 'call':
                if report.passed:
                    self.set_mark(report, MARKS.PASS)
                elif report.failed:
                    report.outcome = "skipped"
                    eval_fail = getattr(item, "_evalxfail", None)
                    if eval_fail is not None:
                        report.wasxfail = eval_fail.getexplanation()
                        self.set_mark(report, MARKS.FAIL)

    def pytest_report_teststatus(self, report):
        mark = getattr(report, BUG, None)
        if mark:
            self.counter(mark)
            return report.outcome, mark.value, report.outcome.upper()

    def pytest_terminal_summary(self, terminalreporter):
        text = []
        if self._skipped:
            text.append('Bugs skipped: %d' % self._skipped)
        if self._passed:
            text.append('Bugs passed: %d' % self._passed)
        if self._failed:
            text.append('Bugs failed: %d' % self._failed)
        if text:
            terminalreporter.write_sep('-', ' '.join(text))
