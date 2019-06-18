from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error checking location header")
def check_location_redirect(request, response):
    redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)
    if redirect_policy and response.get("location"):
        response["location"] = redirect_policy.process_location(
            response.get("location"),
            request.get_host(),
            response.status_code,
            request._tcell_context)
