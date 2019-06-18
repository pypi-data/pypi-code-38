from django.http import HttpResponseForbidden

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.meta import get_appsensor_meta, \
     set_request
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error checking for block rules")
def check_patches_blocking(request):
    patches_policy = TCellAgent.get_policy(PolicyTypes.PATCHES)
    if patches_policy.patches_enabled:
        appsensor_meta = get_appsensor_meta(request)
        set_request(appsensor_meta, request)

        if patches_policy.block_request(appsensor_meta):
            request._tcell_context.ip_blocking_triggered = True
            return HttpResponseForbidden()

    return None
