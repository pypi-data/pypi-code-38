import unittest

from mock import MagicMock, patch

from tcell_agent.instrumentation.djangoinst.middleware_access import \
     is_csrf_middleware_enabled, is_security_middleware_enabled, \
     is_session_middleware_enabled, is_authentication_middleware_enabled, \
     is_session_authentication_middleware_enabled, \
     insert_middleware


COMMON_MIDDLEWARE_LIST = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)


class MiddlewareEnabledTest(unittest.TestCase):
    def middleware_disabled_common(self, func_under_test):
        settings = MagicMock(MIDDLEWARE_CLASSES=list())
        del settings.MIDDLEWARE
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            self.assertFalse(func_under_test())
            self.assertTrue(patched_get_django_settings.called)

    def middleware_enabled_common(self, func_under_test):
        settings = MagicMock(MIDDLEWARE=COMMON_MIDDLEWARE_LIST)
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            self.assertTrue(func_under_test())
            self.assertTrue(patched_get_django_settings.called)

        settings = MagicMock(MIDDLEWARE_CLASSES=COMMON_MIDDLEWARE_LIST)
        del settings.MIDDLEWARE
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            self.assertTrue(func_under_test())
            self.assertTrue(patched_get_django_settings.called)

    def test_csrf_middleware_disabled(self):
        self.middleware_disabled_common(is_csrf_middleware_enabled)

    def test_csrf_middleware_enabled(self):
        self.middleware_enabled_common(is_csrf_middleware_enabled)

    def test_security_middleware_disabled(self):
        self.middleware_disabled_common(is_security_middleware_enabled)

    def test_security_middleware_enabled(self):
        self.middleware_enabled_common(is_security_middleware_enabled)

    def test_session_middleware_disabled(self):
        self.middleware_disabled_common(is_session_middleware_enabled)

    def test_session_middleware_enabled(self):
        self.middleware_enabled_common(is_session_middleware_enabled)

    def test_authentication_middleware_disabled(self):
        self.middleware_disabled_common(is_authentication_middleware_enabled)

    def test_authentication_middleware_enabled(self):
        self.middleware_enabled_common(is_authentication_middleware_enabled)

    def test_session_authentication_middleware_disabled(self):
        self.middleware_disabled_common(is_session_authentication_middleware_enabled)

    def test_session_authentication_middleware_enabled(self):
        self.middleware_enabled_common(is_session_authentication_middleware_enabled)


TEST_MIDDLEWARE_NAME = "tcell_agent.tests.middleware.TestMiddleware"


class InsertMiddlewareTest(unittest.TestCase):
    def test_insert_empty_list(self):
        expected_middleware = (
            TEST_MIDDLEWARE_NAME,
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list()) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME)
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)

        settings = MagicMock()
        del settings.MIDDLEWARE
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list()) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME)
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE_CLASSES, expected_middleware)

    def test_insert_populated_list(self):
        populated_middleware_list = [
            "django.middleware.common.CommonMiddleware"
        ]
        expected_middleware = (
            "django.middleware.common.CommonMiddleware",
            TEST_MIDDLEWARE_NAME,
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME)
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)

        settings = MagicMock()
        del settings.MIDDLEWARE
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME)
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE_CLASSES, expected_middleware)

    def test_insert_after_item(self):
        populated_middleware_list = [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        ]
        expected_middleware = (
            "django.middleware.common.CommonMiddleware",
            TEST_MIDDLEWARE_NAME,
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME,
                                  after="django.middleware.common.CommonMiddleware")
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)

    def test_insert_before_item(self):
        populated_middleware_list = [
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        ]
        expected_middleware = (
            "django.middleware.common.CommonMiddleware",
            TEST_MIDDLEWARE_NAME,
            "django.contrib.auth.middleware.AuthenticationMiddleware"
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME,
                                  before="django.contrib.auth.middleware.AuthenticationMiddleware")
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)

    def test_insert_after_missing_item(self):
        populated_middleware_list = [
            "django.middleware.common.CommonMiddleware"
        ]
        expected_middleware = (
            "django.middleware.common.CommonMiddleware",
            TEST_MIDDLEWARE_NAME,
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME, after="non-existent-middleware")
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)

    def test_insert_before_missing_item(self):
        populated_middleware_list = [
            "django.middleware.common.CommonMiddleware"
        ]
        expected_middleware = (
            TEST_MIDDLEWARE_NAME,
            "django.middleware.common.CommonMiddleware",
        )

        settings = MagicMock()
        del settings.MIDDLEWARE_CLASSES
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_middleware_list",
                       return_value=list(populated_middleware_list)) as patched_get_middleware_list:
                insert_middleware(TEST_MIDDLEWARE_NAME,
                                  before="non-existent-middleware")
                self.assertTrue(patched_get_django_settings.called)
                self.assertTrue(patched_get_middleware_list.called)
                self.assertEqual(settings.MIDDLEWARE, expected_middleware)
