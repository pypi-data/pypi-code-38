from __future__ import print_function
from __future__ import division

import pytest
import civis
from .conftest import mock

from ..cancel import _cancel


@mock.patch('civiscompute.cancel.civis.APIClient')
def test_cancel(client_mock):
    """Test canceling a job."""
    scriptids = [1]
    _cancel(scriptids)
    client_mock.return_value.scripts.post_cancel.assert_called_with(
        scriptids[0])


@mock.patch('civiscompute.cancel.civis.APIClient')
def test_post_cancel_raises(client_mock):
    """Test errors squashed on post cancel."""
    scriptids = [1]
    resp = mock.MagicMock()
    resp.content = None
    resp.reason = 'bad'
    resp.status_code = 502
    client_mock.return_value.scripts.post_cancel.side_effect \
        = civis.base.CivisAPIError(resp)

    with pytest.raises(SystemExit):
        _cancel(scriptids)

    client_mock.return_value.scripts.post_cancel.assert_called_with(
        scriptids[0])
