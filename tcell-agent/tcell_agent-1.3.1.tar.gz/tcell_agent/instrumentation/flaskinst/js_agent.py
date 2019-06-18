import re

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.tcell_logger import get_module_logger


# NOTE: can't use catches_generic_exception since if there is an exception
#       the unmodified response needs to be returned
def insert_js_agent(request, response):
    try:
        if not response.is_streamed and response.headers.get("Content-Type", None) \
           and response.headers["Content-Type"].startswith("text/html"):
            js_agent_policy = TCellAgent.get_policy(PolicyTypes.JS_AGENT)
            script_tag = js_agent_policy.get_js_agent_script_tag(request._tcell_context)
            if script_tag:
                script_tag = "\g<m>{}".format(script_tag)  # noqa pylint: disable=anomalous-backslash-in-string
                response_content = response.get_data(True)
                response_content = re.sub("(?P<m><head>|<head .+?>)", script_tag, response_content)
                from flask.wrappers import Response
                response = Response(response_content, status=response.status_code, headers=response.headers)
    except Exception as exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Error checking for js agent insertion: {}".format(exception))
        LOGGER.exception(exception)

    return response
