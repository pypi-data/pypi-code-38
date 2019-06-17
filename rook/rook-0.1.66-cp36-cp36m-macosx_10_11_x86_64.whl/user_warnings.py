
import threading


class UserWarnings(object):

    _tls = threading.local()

    def __init__(self, reporter):
        self._reporter = reporter
        self._old_value = None

    def __enter__(self):
        self._old_value = self.set_reporter(self._reporter)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_reporter(self._old_value)

    @classmethod
    def set_reporter(cls, warning_reporter):
        if hasattr(cls._tls, "warning_reporter"):
            old_value = cls._tls.warning_reporter
        else:
            old_value = None

        cls._tls.warning_reporter = warning_reporter
        return old_value

    @classmethod
    def send_warning(cls, error):
        if hasattr(cls._tls, "warning_reporter") and cls._tls.warning_reporter:
            cls._tls.warning_reporter.send_warning(error)
