import pytest

from msz_svr_conn import exceptions


def test_incorrectly_raised_request_failure_with_no_error_fields():
    with pytest.raises(exceptions.MisconfiguredException) as context:
        raise exceptions.RequestFailure("some message", {})

    assert str(context.value) == "Error field method was not provided"


def test_incorrectly_raised_auth_failure_with_no_error_fields():
    with pytest.raises(exceptions.MisconfiguredException) as context:
        raise exceptions.AuthFailure("some message", {})

    assert str(context.value) == "Error field status_code was not provided"
