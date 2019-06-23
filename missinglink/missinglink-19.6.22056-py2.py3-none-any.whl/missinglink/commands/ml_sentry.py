import sentry_sdk


class NullContextManager(object):
    def __init__(self, dummy_resource=None):
        self.dummy_resource = dummy_resource

    def __enter__(self):
        return self.dummy_resource

    def __exit__(self, *args):
        pass


def _filter_out_click_processor(event, exc_info):
    from click import ClickException

    if exc_info is None:
        return event

    ex = exc_info[1]

    if isinstance(ex, (ClickException, KeyboardInterrupt)):
        return None

    return event


def __setup_sentry_sdk():
    from missinglink.commands.mali_version import MissinglinkVersion
    from missinglink.commands.global_cli import _VersionChecker

    cli_version = MissinglinkVersion.get_missinglink_cli_version()

    is_dev_version = cli_version is None or cli_version.startswith('0')
    if is_dev_version:
        return NullContextManager()

    client = sentry_sdk.init(
        'https://604d5416743e430b814cd8ac79103201@sentry.io/1289799',
        environment='staging' if _VersionChecker.is_staging(MissinglinkVersion.get_missinglink_package()) else 'prod',
        release=cli_version)

    def ml_callback(_pending, _timeout):
        pass

    sentry_sdk.Hub.current.get_integration('atexit').callback = ml_callback

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag('source', 'ml-cli')
        scope.add_error_processor(_filter_out_click_processor)

    return client


def sentry_capture_exceptions(method):
    def wrap(*args, **kwargs):
        from sentry_sdk import capture_exception

        with __setup_sentry_sdk():
            try:
                return method(*args, **kwargs)
            except Exception:
                capture_exception()
                raise

    return wrap
