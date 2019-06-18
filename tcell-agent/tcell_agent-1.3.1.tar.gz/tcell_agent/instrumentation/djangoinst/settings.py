# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import json

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import safe_wrap_function
from tcell_agent.instrumentation.djangoinst.config import get_django_settings
from tcell_agent.instrumentation.djangoinst.middleware_access import \
     is_csrf_middleware_enabled, is_security_middleware_enabled, is_session_middleware_enabled, \
     is_authentication_middleware_enabled, is_session_authentication_middleware_enabled
from tcell_agent.events.app_config_settings import AppConfigSettings


def send_django_setting_events():
    settings = get_django_settings()

    safe_wrap_function(
        "Settings: Check cookie session length",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_COOKIE_HTTPONLY",
            settings.SESSION_COOKIE_HTTPONLY
        ))
    )
    safe_wrap_function(
        "Settings: Check cookie session secure",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_COOKIE_SECURE",
            settings.SESSION_COOKIE_SECURE
        ))
    )
    safe_wrap_function(
        "Settings: Check cookie session expiration",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Session",
            "SESSION_EXPIRE_AT_BROWSER_CLOSE",
            settings.SESSION_EXPIRE_AT_BROWSER_CLOSE
        ))
    )
    safe_wrap_function(
        "Settings: Debug turned off",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "DEBUG",
            settings.DEBUG
        ))
    )
    safe_wrap_function(
        "Settings: Allowed Host Length",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "ALLOWED_HOSTS_LEN",
            len(settings.ALLOWED_HOSTS)
        ))
    )
    safe_wrap_function(
        "Settings: List of password hashes",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Auth",
            "PASSWORD_HASHERS",
            json.dumps(settings.PASSWORD_HASHERS)
        ))
    )
    safe_wrap_function(
        "Settings: Password reset timeout in days",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Auth",
            "PASSWORD_RESET_TIMEOUT_DAYS",
            settings.PASSWORD_RESET_TIMEOUT_DAYS
        ))
    )
    safe_wrap_function(
        "Settings: CsrfViewMiddleware enabled",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "csrf_protection",
            is_csrf_middleware_enabled()
        ))
    )
    safe_wrap_function(
        "Settings: SecurityMiddleware enabled",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "security_middleware",
            is_security_middleware_enabled()
        ))
    )
    safe_wrap_function(
        "Settings: SessionMiddleware enabled",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "session_middleware",
            is_session_middleware_enabled()
        ))
    )
    safe_wrap_function(
        "Settings: AuthenticationMiddleware",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "authentication_middleware",
            is_authentication_middleware_enabled()
        ))
    )
    safe_wrap_function(
        "Settings: SessionAuthenticationMiddleware enabled",
        lambda: TCellAgent.send(AppConfigSettings(
            "Django",
            "Core",
            "session_authentication_middleware",
            is_session_authentication_middleware_enabled()
        ))
    )
