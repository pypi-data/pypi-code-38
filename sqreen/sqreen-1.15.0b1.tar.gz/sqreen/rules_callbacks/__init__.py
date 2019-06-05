# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Contains all callback classes
"""
import logging
import sys

from ..remote_exception import RemoteException
from ..rules import RuleCallback
from ..runtime_storage import runtime
from ..signature import REQUIRED_KEYS, SIGNATURE_VERSION, InvalidSignature
from ..utils import HAS_ASYNCIO
from .auth_metrics import AuthMetricsCB
from .binding_accessor_counter import BindingAccessorCounter
from .binding_accessor_matcher import BindingAccessorMatcherCallback
from .count_http_codes import CountHTTPCodesCB
from .count_http_codes_django import CountHTTPCodesCBDjango
from .count_http_codes_flask import CountHTTPCodesCBFlask
from .count_http_codes_php import CountHTTPCodesCBPHP
from .count_http_codes_pyramid import CountHTTPCodesCBPyramid
from .crawler_user_agent_matches_metrics import (
    CrawlerUserAgentMatchesMetricsCB,
)
from .extension_passthru import ExtensionPassthruCB
from .headers_insert import HeadersInsertCB
from .headers_insert_django import HeadersInsertCBDjango
from .headers_insert_flask import HeadersInsertCBFlask
from .headers_insert_pyramid import HeadersInsertCBPyramid
from .ip_blacklist import IPBlacklistCB
from .not_found import NotFoundCB
from .not_found_django import NotFoundCBDjango
from .not_found_flask import NotFoundCBFlask
# Import rules callbacks
from .record_request_context import RecordRequestContext
from .record_request_context_django import RecordRequestContextDjango
from .record_request_context_flask import RecordRequestContextFlask
from .record_request_context_pyramid import RecordRequestContextPyramid
from .reflected_xss import ReflectedXSSCB
from .regexp_rule import RegexpRule
from .shell_env import ShellEnvCB
from .sqreen_error_page_django import SqreenErrorPageDjango
from .sqreen_error_page_django_new_style import SqreenErrorPageDjangoNewStyle
from .sqreen_error_page_flask import SqreenErrorPageFlask
from .sqreen_error_page_pyramid import SqreenErrorPagePyramid
from .user_agent_matches import UserAgentMatchesCB
from .user_agent_matches_framework import (
    UserAgentMatchesCBDjango,
    UserAgentMatchesCBFramework,
)

# Workaround for Jenkins build.
try:
    from .js import JSCB
except ImportError:
    pass

if HAS_ASYNCIO:
    from .record_request_context_aiohttp import RecordRequestContextAioHTTP
    from .headers_insert_aiohttp import HeadersInsertCBAioHTTP
    from .count_http_codes_aiohttp import CountHTTPCodesCBAioHTTP
    from .sqreen_error_page_aiohttp import SqreenErrorPageAioHTTP


LOGGER = logging.getLogger(__name__)


def cb_from_rule(rule, runner, rule_verifier=None, storage=runtime):
    """ Instantiate the right cb class
    """
    # Fixme clean

    if not isinstance(rule, dict):
        LOGGER.debug("Invalid rule type %s", type(rule))
        return

    # Check rule signature
    if rule_verifier is not None:
        try:
            rule_verifier.verify_rule(rule, REQUIRED_KEYS, SIGNATURE_VERSION)
        except InvalidSignature as exc:
            LOGGER.critical("Can't verify signature of rule %s", rule["name"])
            exc.callback_payload["rule_name"] = rule["name"]
            exc.callback_payload["rulespack_id"] = rule["rulespack_id"]
            raise

    # Ask for native attack rendering
    if "attack_render_info" in rule.get("hookpoint", {}):
        callback_class_name = "ExtensionPassthruCB"

    # Use JSCB for internal_js_hook callback used in PHP
    elif rule.get("hookpoint", {}).get("strategy") == "internal_js_hook":
        callback_class_name = "JSCB"

    else:
        callback_class_name = rule.get("hookpoint", {}).get("callback_class")

    if callback_class_name is None:
        err_msg = (
            "Couldn't find a callback_class_name for rule %s, fallback on js"
        )
        LOGGER.debug(err_msg, rule["name"])
        callback_class_name = "JSCB"

    possible_subclass = globals().get(callback_class_name, None)

    if possible_subclass and issubclass(possible_subclass, RuleCallback):
        try:
            return possible_subclass.from_rule_dict(rule, runner, storage=storage)
        except Exception:
            LOGGER.warning(
                "Couldn't instantiate a callback for rule %s",
                rule,
                exc_info=True,
            )
            infos = {
                "rule_name": rule["name"],
                "rulespack_id": rule["rulespack_id"],
            }
            remote_exception = RemoteException(sys.exc_info(), infos)
            runner.queue.put(remote_exception)
            return

    LOGGER.debug(
        "Couldn't find the class matching class_name %s", callback_class_name
    )
    return


__all__ = [
    "AuthMetricsCB",
    "BindingAccessorCounter",
    "BindingAccessorMatcherCallback",
    "cb_from_rule",
    "CountHTTPCodesCB",
    "CountHTTPCodesCBAioHTTP",
    "CountHTTPCodesCBDjango",
    "CountHTTPCodesCBFlask",
    "CountHTTPCodesCBPHP",
    "CountHTTPCodesCBPyramid",
    "CrawlerUserAgentMatchesMetricsCB",
    "ExtensionPassthruCB",
    "HeadersInsertCB",
    "HeadersInsertCBAioHTTP",
    "HeadersInsertCBDjango",
    "HeadersInsertCBFlask",
    "HeadersInsertCBPyramid",
    "IPBlacklistCB",
    "JSCB",
    "NotFoundCB",
    "NotFoundCBDjango",
    "NotFoundCBFlask",
    "RecordRequestContext",
    "RecordRequestContextAioHTTP",
    "RecordRequestContextDjango",
    "RecordRequestContextFlask",
    "RecordRequestContextPyramid",
    "ReflectedXSSCB",
    "RegexpRule",
    "ShellEnvCB",
    "SqreenErrorPageAioHTTP",
    "SqreenErrorPageDjango",
    "SqreenErrorPageDjangoNewStyle",
    "SqreenErrorPageFlask",
    "SqreenErrorPagePyramid",
    "UserAgentMatchesCB",
    "UserAgentMatchesCBDjango",
    "UserAgentMatchesCBFramework",
]
