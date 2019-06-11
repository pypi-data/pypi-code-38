import re
import warnings
from contextlib import contextmanager
from functools import partial

import pytest
import pytest_regtest


@pytest.fixture
def record_warnings(monkeypatch):
    def record(messages, warning_exception, *a, **kw):
        text = str(warning_exception)
        if "Use get_result() which forces correct exception handling" in text:
            # this is a warning triggered by bug in pytest.
            return
        messages.append(text)

    @contextmanager
    def manager():
        messages = []
        monkeypatch.setattr(warnings, "warn", partial(record, messages))
        yield messages
        monkeypatch.undo()

    yield manager


@pytest_regtest.register_converter_post
def fix_time_strings(output, request):
    output = re.sub(r"\d{2}:\d{2}:\d{2}\.\d", "<h:m:s.ms>", output)
    return output
