from tcell_agent.policies.http_redirect_policy import HttpRedirectPolicy
from tcell_agent.policies.dataloss_policy import DataLossPolicy
from tcell_agent.policies.login_policy import LoginPolicy
from tcell_agent.policies.appfirewall_policy import AppfirewallPolicy
from tcell_agent.policies.command_injection_policy import CommandInjectionPolicy
from tcell_agent.policies.headers_policy import HeadersPolicy
from tcell_agent.policies.js_agent_policy import JsAgentPolicy
from tcell_agent.policies.patches_policy import PatchesPolicy
from tcell_agent.policies.system_enablements import SystemEnablements


class PolicyTypes(object):
    HTTP_REDIRECT = HttpRedirectPolicy.api_identifier
    HEADERS = HeadersPolicy.api_identifier
    DATALOSS = DataLossPolicy.api_identifier
    APPSENSOR = AppfirewallPolicy.api_identifier
    LOGIN = LoginPolicy.api_identifier
    PATCHES = PatchesPolicy.api_identifier
    COMMAND_INJECTION = CommandInjectionPolicy.api_identifier
    JS_AGENT = JsAgentPolicy.api_identifier
    SYSTEM_ENABLEMENTS = SystemEnablements.api_identifier
