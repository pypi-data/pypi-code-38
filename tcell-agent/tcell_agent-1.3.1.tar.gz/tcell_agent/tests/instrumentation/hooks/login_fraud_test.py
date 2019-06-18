import sys

# features from py 3.0 are used in order to set up the tests properly
if sys.version_info >= (3, 0):
    import unittest

    from types import ModuleType

    from mock import MagicMock, patch

    from tcell_agent.agent import TCellAgent
    from tcell_agent.config.configuration import set_config
    from tcell_agent.instrumentation.hooks.login_fraud import _instrument
    from tcell_agent.policies.login_policy import LoginPolicy
    from tcell_agent.tests.support.builders import ConfigurationBuilder

    def send_login_event(status,  # pylint: disable=unused-argument
                         session_id,  # pylint: disable=unused-argument
                         user_agent,  # pylint: disable=unused-argument
                         referrer,  # pylint: disable=unused-argument
                         remote_address,  # pylint: disable=unused-argument
                         header_keys,  # pylint: disable=unused-argument
                         user_id,  # pylint: disable=unused-argument
                         document_uri,  # pylint: disable=unused-argument
                         user_valid=None):  # pylint: disable=unused-argument
        pass

    def send_django_login_event(status, django_request, user_id, session_id, user_valid=None):   # pylint: disable=unused-argument
        pass

    def send_flask_login_event(status, flask_request, user_id, session_id, user_valid=None):  # pylint: disable=unused-argument
        pass


    m_login = ModuleType("tcell_hooks")  # noqa
    mv_login = ModuleType("v1")  # noqa

    # pylint: disable=no-member
    class HooksTest(unittest.TestCase):  # noqa
        @classmethod
        def setUpClass(cls):
            m_login.__file__ = m_login.__name__ + ".py"
            m_login.__path__ = []
            mv_login.__file__ = mv_login.__name__ + ".py"
            sys.modules["tcell_hooks"] = m_login
            sys.modules["tcell_hooks.v1"] = mv_login

            setattr(m_login, "v1", mv_login)
            setattr(mv_login, "LOGIN_SUCCESS", "success")
            setattr(mv_login, "LOGIN_FAILURE", "failure")
            setattr(mv_login, "send_login_event", send_login_event)
            setattr(mv_login, "send_django_login_event", send_django_login_event)
            setattr(mv_login, "send_flask_login_event", send_flask_login_event)

            _instrument()

        @classmethod
        def tearDownClass(cls):
            del sys.modules["tcell_hooks"]
            del sys.modules["tcell_hooks.v1"]

        def setUp(self):
            configuration = ConfigurationBuilder().build()
            set_config(configuration)
            self.login_policy = LoginPolicy(
                None,
                {"login_success_enabled": True, "login_failed_enabled": True},
                None)

        def tearDown(self):
            set_config(None)

        def test_login_success_hooks(self):
            with patch.object(self.login_policy, "report_login_success", return_value=None) \
                    as patched_report_login_success:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_SUCCESS,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertTrue(patched_report_login_success.called)
                    _, kwargs = patched_report_login_success.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "tcell_context", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT", "REFERER"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, "http://192.168.99.100:3000/")

        def test_login_failure_hooks(self):
            with patch.object(self.login_policy, "report_login_failure", return_value=None) \
                    as patched_report_login_failure:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_FAILURE,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertTrue(patched_report_login_failure.called)
                    _, kwargs = patched_report_login_failure.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "user_valid", "tcell_context", "password", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(kwargs["user_valid"], None)
                    self.assertEqual(kwargs["password"], None)
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT", "REFERER"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, "http://192.168.99.100:3000/")

        def test_django_login_success_hooks(self):
            django_request = MagicMock(
                "FakeRequest",
                META={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                    "HTTP_REFERER": "http://192.168.99.100:3000/"})
            django_request.get_full_path = MagicMock(return_value="/users/auth/doorkeeper/callbackuri")

            with patch.object(self.login_policy, "report_login_success", return_value=None) \
                    as patched_report_login_success:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_django_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_django_login_event(
                        mv_login.LOGIN_SUCCESS,
                        django_request,
                        "tcell@tcell.io",
                        "124KDJFL3234",
                        password="admin123")

                    self.assertTrue(patched_report_login_success.called)
                    _, kwargs = patched_report_login_success.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "tcell_context", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT", "REFERER"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, "http://192.168.99.100:3000/")

        def test_django_login_failure_hooks(self):
            django_request = MagicMock(
                "FakeRequest",
                META={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                    "HTTP_REFERER": "http://192.168.99.100:3000/"})
            django_request.get_full_path = MagicMock(return_value="/users/auth/doorkeeper/callbackuri")

            with patch.object(self.login_policy, "report_login_failure", return_value=None) \
                    as patched_report_login_failure:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_django_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_django_login_event(
                        mv_login.LOGIN_FAILURE,
                        django_request,
                        "tcell@tcell.io",
                        "124KDJFL3234",
                        user_valid=True,
                        password="admin123")

                    self.assertTrue(patched_report_login_failure.called)
                    _, kwargs = patched_report_login_failure.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "user_valid", "tcell_context", "password", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(kwargs["user_valid"], True)
                    self.assertEqual(kwargs["password"], "admin123")
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT", "REFERER"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, "http://192.168.99.100:3000/")

        def test_flask_login_success_hooks(self):
            flask_request = MagicMock(
                "FakeRequest",
                url="/users/auth/doorkeeper/callbackuri",
                environ={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})

            with patch.object(self.login_policy, "report_login_success", return_value=None) \
                    as patched_report_login_success:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_flask_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_flask_login_event(
                        mv_login.LOGIN_SUCCESS,
                        flask_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_report_login_success.called)
                    _, kwargs = patched_report_login_success.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "tcell_context", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, None)

        def test_flask_login_failure_hooks(self):
            flask_request = MagicMock(
                "FakeRequest",
                url="/users/auth/doorkeeper/callbackuri",
                environ={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})

            with patch.object(self.login_policy, "report_login_failure", return_value=None) \
                    as patched_report_login_failure:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_flask_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_flask_login_event(
                        mv_login.LOGIN_FAILURE,
                        flask_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_report_login_failure.called)
                    _, kwargs = patched_report_login_failure.call_args
                    self.assertEqual(set(kwargs.keys()), set(["user_id", "user_valid", "tcell_context", "password", "header_keys"]))
                    self.assertEqual(kwargs["user_id"], "tcell@tcell.io")
                    self.assertEqual(kwargs["user_valid"], None)
                    self.assertEqual(kwargs["password"], None)
                    self.assertEqual(set(kwargs["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(kwargs["tcell_context"].user_agent, "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")
                    self.assertEqual(kwargs["tcell_context"].remote_address, "192.168.99.1")
                    self.assertEqual(kwargs["tcell_context"].session_id, "124KDJFL3234")
                    self.assertEqual(kwargs["tcell_context"].fullpath, "/users/auth/doorkeeper/callbackuri")
                    self.assertEqual(kwargs["tcell_context"].referrer, None)

        def test_unknown_status_hooks(self):
            mock_logger = MagicMock()
            mock_logger.error.return_value = None

            with patch.object(self.login_policy, "report_login_failure", return_value=None) \
                    as patched_report_login_failure:
                with patch.object(self.login_policy, "report_login_success", return_value=None) \
                        as patched_report_login_success:
                    with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                        with patch("tcell_agent.instrumentation.hooks.login_fraud.get_logger") as patched_get_logger:
                            patched_get_logger.return_value = mock_logger

                            from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,redefined-outer-name
                            send_login_event(
                                "blergh",
                                "124KDJFL3234",
                                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                                "http://192.168.99.100:3000/",
                                "192.168.99.1",
                                ["HOST", "USER_AGENT", "REFERER"],
                                "tcell@tcell.io",
                                "/users/auth/doorkeeper/callbackuri")

                            self.assertFalse(patched_report_login_success.called)
                            self.assertFalse(patched_report_login_failure.called)
                            mock_logger.error.assert_called_once_with("Unkown login status: blergh")

        def test_login_success_disabled_login_send(self):
            self.login_policy.login_success_enabled = False
            with patch.object(self.login_policy, "report_login_success", return_value=None) \
                    as patched_report_login_success:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_SUCCESS,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_report_login_success.called)

        def test_login_failed_disabled_login_send(self):
            self.login_policy.login_failed_enabled = False
            with patch.object(self.login_policy, "report_login_failure", return_value=None) \
                    as patched_report_login_failure:
                with patch.object(TCellAgent, "get_policy", return_value=self.login_policy):
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_FAILURE,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_report_login_failure.called)
