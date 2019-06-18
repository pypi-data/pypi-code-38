from tcell_agent.policies.appfirewall_policy import AppfirewallPolicy
from tcell_agent.policies.command_injection_policy import CommandInjectionPolicy
from tcell_agent.policies.dataloss_policy import DataLossPolicy
from tcell_agent.policies.headers_policy import HeadersPolicy
from tcell_agent.policies.http_redirect_policy import HttpRedirectPolicy
from tcell_agent.policies.js_agent_policy import JsAgentPolicy
from tcell_agent.policies.login_policy import LoginPolicy
from tcell_agent.policies.patches_policy import PatchesPolicy
from tcell_agent.policies.system_enablements import SystemEnablements

from tcell_agent.policies.policy_types import PolicyTypes
from tcell_agent.tcell_logger import get_module_logger


RUST_POLICY_CLASSES = [HttpRedirectPolicy,
                       LoginPolicy,
                       AppfirewallPolicy,
                       CommandInjectionPolicy,
                       HeadersPolicy,
                       JsAgentPolicy,
                       PatchesPolicy,
                       SystemEnablements]


class PoliciesManager(object):
    def __init__(self, native_agent):
        get_module_logger(__name__).info("Initializing Policies")
        self.native_agent = native_agent
        self.policies = {}

        self.policies[PolicyTypes.DATALOSS] = DataLossPolicy(None,
                                                             None,
                                                             None)
        for policy_class in RUST_POLICY_CLASSES:
            self.policies[policy_class.api_identifier] = policy_class(self.native_agent,
                                                                      None,
                                                                      None)

    def get(self, policy_type):
        return self.policies.get(policy_type)

    def update_native_agent(self, native_agent):
        for policy_class in RUST_POLICY_CLASSES:
            self.policies[policy_class.api_identifier].native_agent = native_agent

        self.native_agent = native_agent

    def create_policy(self, policy_class, enablements, policy_json):
        try:
            return policy_class(self.native_agent,
                                enablements,
                                policy_json)
        except Exception as general_exception:
            LOGGER = get_module_logger(__name__)
            LOGGER.error("Exception parsing {} policy".format(policy_class))
            LOGGER.exception(general_exception)

        return policy_class(self.native_agent,
                            None,
                            None)

    def process_policies(self, enablements, policies_json):
        if not policies_json:
            return

        for policy_class in RUST_POLICY_CLASSES:
            self.policies[policy_class.api_identifier] = self.create_policy(policy_class,
                                                                            enablements,
                                                                            policies_json)

        policy_type = PolicyTypes.DATALOSS
        dlp_policy_json = policies_json.get(policy_type)
        if dlp_policy_json:
            self.policies[policy_type] = self.create_policy(DataLossPolicy,
                                                            None,
                                                            dlp_policy_json)
