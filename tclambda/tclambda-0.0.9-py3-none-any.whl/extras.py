import time
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class Value:
    value: float


@contextmanager
def timeme():
    start_time = time.monotonic()
    value = Value(0)
    try:
        yield value
    finally:
        value.value = time.monotonic() - start_time


def sentry_init():  # pragma: no cover
    try:
        import sentry_sdk
        from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
    except ImportError:
        pass
    else:
        # The Sentry DSN is set in the SENTRY_DSN environmental variable
        sentry_sdk.init(integrations=[AwsLambdaIntegration()])
