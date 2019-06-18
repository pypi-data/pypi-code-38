import unittest

from mock import call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.djangoinst.settings import send_django_setting_events


class FakeSettings(object):
    def __init__(self):
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SECURE = True
        self.SESSION_EXPIRE_AT_BROWSER_CLOSE = True
        self.DEBUG = True
        self.DEBUG = True

        self.ALLOWED_HOSTS = ["*"]
        self.PASSWORD_HASHERS = ["hasher"]
        self.PASSWORD_RESET_TIMEOUT_DAYS = 3

        self.MIDDLEWARE_CLASSES = (
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        )


class SettingsTest(unittest.TestCase):
    def test_settings(self):
        settings = FakeSettings()
        with patch("tcell_agent.instrumentation.djangoinst.middleware_access.get_django_settings",
                   return_value=settings) as patched_get_django_settings:
            with patch("tcell_agent.instrumentation.djangoinst.settings.get_django_settings",
                       return_value=settings) as patched_get_django_settings:
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    send_django_setting_events()
                    self.assertTrue(patched_get_django_settings.called)
                    self.assertTrue(patched_send.called)

                    self.assertEqual(
                        patched_send.mock_calls,
                        [call({"event_type": "app_config_setting", "package": "Django", "section": "Session", "name": "SESSION_COOKIE_HTTPONLY", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Session", "name": "SESSION_COOKIE_SECURE", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Session", "name": "SESSION_EXPIRE_AT_BROWSER_CLOSE", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "DEBUG", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "ALLOWED_HOSTS_LEN", "value": "1"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Auth", "name": "PASSWORD_HASHERS", "value": "[\"hasher\"]"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Auth", "name": "PASSWORD_RESET_TIMEOUT_DAYS", "value": "3"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "csrf_protection", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "security_middleware", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "session_middleware", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "authentication_middleware", "value": "true"}),
                         call({"event_type": "app_config_setting", "package": "Django", "section": "Core", "name": "session_authentication_middleware", "value": "true"})]
                    )
