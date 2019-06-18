_needs_instrumention = True
_agent_has_started = False
_default_charset = "utf-8"
_test_mode = False
_django_active = False
_flask_active = False


def needs_instrumentation():
    return _needs_instrumention


def set_has_been_instrumented():
    global _needs_instrumention  # pylint: disable=global-statement
    _needs_instrumention = False


def has_agent_started():
    return _agent_has_started


def set_agent_has_started():
    global _agent_has_started  # pylint: disable=global-statement
    _agent_has_started = True


def get_default_charset():
    return _default_charset


def update_default_charset(charset):
    global _default_charset  # pylint: disable=global-statement
    _default_charset = charset


def get_test_mode():
    return _test_mode


def enable_test_mode():
    global _test_mode  # pylint: disable=global-statement
    _test_mode = True


def django_active():
    return _django_active


def flask_active():
    return _flask_active


try:
    import django  # pylint: disable=unused-import
    _django_active = True

except ImportError:
    pass

try:
    from flask import Flask  # pylint: disable=unused-import
    _flask_active = True
except ImportError:
    pass
