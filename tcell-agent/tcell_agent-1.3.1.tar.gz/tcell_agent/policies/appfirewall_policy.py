from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class AppfirewallPolicy(TCellPolicy):
    api_identifier = "appsensor"

    def __init__(self, native_agent, enablements, policies_json):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.instrument_database_queries = False
        self.appfirewall_enabled = False

        self.update_enablements(enablements, policies_json)

    def update_enablements(self, enablements, policies_json):
        if not policies_json:
            policies_json = {}
        if not enablements:
            enablements = {}

        # database instrumentation is sketchy at best, so don't instrument it unless absolutely necessary
        # this check means database unusual result size is enabled, so database needs to be instrumented
        self.instrument_database_queries = "database" in policies_json.get(
            "appsensor", {}
        ).get(
            "data", {}
        ).get(
            "sensors", {}
        )

        self.appfirewall_enabled = enablements.get("appfirewall", False)

    def check_appfirewall_injections(self, appsensor_meta):
        if not self.appfirewall_enabled:
            return None

        return self.native_agent.apply_appfirewall(appsensor_meta)
