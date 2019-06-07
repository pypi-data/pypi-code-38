import io
import logging
import textwrap
import sys
import unittest
import warnings


TEST_MODULES = [
    'mockry.test.import_test',
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


def test_runner_factory(stderr):
    class MockryTextTestRunner(unittest.TextTestRunner):
        def __init__(self, *args, **kwargs):
            kwargs['stream'] = stderr
            super(MockryTextTestRunner, self).__init__(*args, **kwargs)

        def run(self, test):
            result = super(MockryTextTestRunner, self).run(test)
            if result.skipped:
                skip_reasons = set(reason for (test, reason) in result.skipped)
                self.stream.write(
                    textwrap.fill(
                        'Some tests were skipped because: %s'
                        % ', '.join(sorted(skip_reasons))
                    )
                )
                self.stream.write('\n')
            return result

    return MockryTextTestRunner


class LogCounter(logging.Filter):
    """Counts the number of WARNING or higher log records."""

    def __init__(self, *args, **kwargs):
        super(LogCounter, self).__init__(*args, **kwargs)
        self.info_count = self.warning_count = self.error_count = 0

    def filter(self, record):
        if record.levelno >= logging.ERROR:
            self.error_count += 1
        elif record.levelno >= logging.WARNING:
            self.warning_count += 1
        elif record.levelno >= logging.INFO:
            self.info_count += 1
        return True


class CountingStderr(io.IOBase):
    def __init__(self, real):
        self.real = real
        self.byte_count = 0

    def write(self, data):
        self.byte_count += len(data)
        return self.real.write(data)

    def flush(self):
        return self.real.flush()


def main():
    # Be strict about most warnings (This is set in our test running
    # scripts to catch import-time warnings, but set it again here to
    # be sure). This also turns on warnings that are ignored by
    # default, including DeprecationWarnings and python 3.2's
    # ResourceWarnings.
    warnings.filterwarnings('error')
    # setuptools sometimes gives ImportWarnings about things that are on
    # sys.path even if they're not being used.
    warnings.filterwarnings('ignore', category=ImportWarning)
    # Tornado generally shouldn't use anything deprecated, but some of
    # our dependencies do (last match wins).
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('error', category=DeprecationWarning, module=r'tort\..*')
    warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
    warnings.filterwarnings(
        'error', category=PendingDeprecationWarning, module=r'tort\..*'
    )

    logging.getLogger('tornado.access').setLevel(logging.CRITICAL)

    # Certain errors (especially 'unclosed resource' errors raised in
    # destructors) go directly to stderr instead of logging. Count
    # anything written by anything but the test runner as an error.
    orig_stderr = sys.stderr
    counting_stderr = CountingStderr(orig_stderr)
    sys.stderr = counting_stderr  # type: ignore

    import tornado.testing

    kwargs = {}

    # HACK:  unittest.main will make its own changes to the warning
    # configuration, which may conflict with the settings above
    # or command-line flags like -bb.  Passing warnings=False
    # suppresses this behavior, although this looks like an implementation
    # detail.  http://bugs.python.org/issue15626
    kwargs['warnings'] = False

    kwargs['testRunner'] = test_runner_factory(orig_stderr)
    tornado.testing.main(**kwargs)


if __name__ == '__main__':
    main()
