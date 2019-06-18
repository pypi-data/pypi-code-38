from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error checking for block rules")
def check_patches_blocking(request):
    request._ip_blocking_triggered = False

    patches_policy = TCellAgent.get_policy(PolicyTypes.PATCHES)
    if patches_policy.patches_enabled and \
       patches_policy.block_request(request._appsensor_meta):
        request._ip_blocking_triggered = True
        from flask.wrappers import Response
        return Response("", 403)

    return None
