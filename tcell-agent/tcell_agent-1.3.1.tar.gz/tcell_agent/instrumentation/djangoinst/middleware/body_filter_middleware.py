# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import re

from django.http import HttpResponse

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.tcell_logger import get_module_logger

head_tag_regexp = re.compile(b"(?P<m><head>|<head .+?>)")


def add_tag(request, response):
    try:
        if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
            if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
                js_agent_policy = TCellAgent.get_policy(PolicyTypes.JS_AGENT)
                script_tag = js_agent_policy.get_js_agent_script_tag(request._tcell_context)
                if script_tag:
                    script_tag = "\g<m>{}".format(script_tag)  # noqa pylint: disable=anomalous-backslash-in-string
                    if not isinstance(response.content, str):
                        script_tag = script_tag.encode("utf-8")

                    response_type = type(response.content)
                    try:
                        if response_type == str:
                            response.content = re.sub(head_tag_regexp, script_tag, response.content.decode("utf8"), count=1)

                        else:
                            response.content = re.sub(head_tag_regexp, script_tag, response.content, count=1)
                    except UnicodeDecodeError:
                        pass
    except Exception as exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Error checking for js agent insertion: {}".format(exception))
        LOGGER.exception(exception)


class BodyFilterMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return self.process_response(request, response)

    def process_response(self, request, response):  # pylint: disable=no-self-use
        add_tag(request, response)
        return response
