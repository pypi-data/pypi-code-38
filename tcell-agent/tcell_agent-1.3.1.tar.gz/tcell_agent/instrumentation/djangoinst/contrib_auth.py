# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.config.configuration import get_config
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.utils import header_keys_from_request_env
from tcell_agent.tcell_logger import get_module_logger


def extract_username(user, request):
    username = None
    try:
        username = user.get_username()
    except Exception:
        pass
    if request:
        try:
            if request.method == "POST":
                username = request.POST.get("user", username)
                username = request.POST.get("email", username)
                username = request.POST.get("email_address", username)
                username = request.POST.get("username", username)
            else:
                username = request.GET.get("username", username)
        except Exception as e:
            LOGGER = get_module_logger(__name__)
            LOGGER.error("Could not determine username for login success event: {e}".format(e=e))
            LOGGER.exception(e)

    return username


def extract_username_password(credentials, request):
    username = None
    password = None
    if credentials:
        username = credentials.get("username")

    try:
        if request.method == "POST":
            password = request.POST.get("password")
        else:
            password = request.GET.get("password")
    except Exception as e:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Could not determine password for login failure event: {e}".format(e=e))
        LOGGER.exception(e)

    return [username, password]


@catches_generic_exception(__name__, "Error reporting login success")
def report_user_logged_in(sender, user, request, **kwargs):  # pylint: disable=unused-argument
    if not get_config().should_instrument_django_auth():
        return

    login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
    if not login_policy.login_success_enabled:
        return

    request = GlobalRequestMiddleware.get_current_request()
    if not request:
        return

    username = extract_username(user, request)
    tcell_context = request._tcell_context
    tcell_context.user_id = username

    login_policy.report_login_success(
        user_id=username,
        header_keys=header_keys_from_request_env(request.META),
        tcell_context=tcell_context)


@catches_generic_exception(__name__, "Error reporting login failure")
def report_user_login_failed(sender, credentials, **kwargs):  # pylint: disable=unused-argument
    if not get_config().should_instrument_django_auth():
        return

    login_policy = TCellAgent.get_policy(PolicyTypes.LOGIN)
    if not login_policy.login_failed_enabled:
        return

    request = GlobalRequestMiddleware.get_current_request()
    if not request:
        return

    username, password = extract_username_password(credentials, request)
    tcell_context = request._tcell_context
    tcell_context.user_id = username

    login_policy.report_login_failure(
        user_id=username,
        password=password,
        header_keys=header_keys_from_request_env(request.META),
        user_valid=None,
        tcell_context=tcell_context)


try:
    import django  # noqa pylint: disable=unused-import
    from django.contrib.auth.forms import AuthenticationForm  # noqa pylint: disable=unused-import

    if TCellAgent.tCell_agent:
        from django.contrib.auth.signals import user_logged_in, user_login_failed
        from django.db.backends.signals import connection_created  # noqa pylint: disable=unused-import

        user_logged_in.connect(report_user_logged_in)
        user_login_failed.connect(report_user_login_failed)
except Exception as e:
    get_module_logger(__name__).debug("Could not instrument django common-auth")
    get_module_logger(__name__).exception(e)
