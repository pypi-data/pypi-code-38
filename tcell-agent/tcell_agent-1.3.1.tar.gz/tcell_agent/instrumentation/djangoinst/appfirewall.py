from __future__ import unicode_literals


from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.meta import get_appsensor_meta, \
     set_request, set_response
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error processing appfirewall")
def inspect_request_response(django_response_class, request, response):
    if request._tcell_context.ip_blocking_triggered:
        return

    appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appfirewall_policy.appfirewall_enabled:
        appsensor_meta = get_appsensor_meta(request)
        set_request(appsensor_meta, request)
        set_response(appsensor_meta, django_response_class, response)
        appfirewall_policy.check_appfirewall_injections(appsensor_meta)
