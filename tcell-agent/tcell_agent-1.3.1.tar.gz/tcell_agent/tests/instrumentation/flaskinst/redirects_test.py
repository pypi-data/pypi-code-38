import unittest

from mock import Mock, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.instrumentation.flaskinst.redirects import check_location_redirect
from tcell_agent.tests.support.builders import ContextBuilder


class FlaskRedirectsTest(unittest.TestCase):
    def test_check_location_redirect(self):
        context = ContextBuilder().build()
        request = Mock(host="host", _tcell_context=context)
        response = Mock(headers={}, location="/redirect", status_code=200)
        redirect_policy = Mock()
        redirect_policy.process_location = Mock(return_value="/redirect")

        with patch.object(TCellAgent, "get_policy", return_value=redirect_policy) as patched_get_policy:
            check_location_redirect(request, response)

            patched_get_policy.assert_called_once_with(PolicyTypes.HTTP_REDIRECT)
            redirect_policy.process_location.assert_called_once_with(
                "/redirect",
                "host",
                200,
                context)

            self.assertEqual(response.headers["location"], "/redirect")
