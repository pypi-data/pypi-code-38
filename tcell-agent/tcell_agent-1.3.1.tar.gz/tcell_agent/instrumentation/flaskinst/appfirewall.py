from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.flaskinst.meta import update_meta_with_response
from tcell_agent.policies.policy_types import PolicyTypes


@catches_generic_exception(__name__, "Error processing appfirewall")
def run_appfirewall_check(request, response, response_code):
    if request._ip_blocking_triggered:
        return

    appfirewall_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appfirewall_policy.appfirewall_enabled:
        appsensor_meta = request._appsensor_meta
        update_meta_with_response(appsensor_meta, response, response_code)
        appfirewall_policy.check_appfirewall_injections(appsensor_meta)
