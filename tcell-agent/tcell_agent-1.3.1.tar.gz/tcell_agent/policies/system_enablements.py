from tcell_agent.policies.base_policy import TCellPolicy


class SystemEnablements(TCellPolicy):
    api_identifier = "system_enablements"

    def __init__(self, _native_agent, enablements, _policy_json):
        TCellPolicy.__init__(self)
        self.send_routes_enabled = True
        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}
        self.send_routes_enabled = enablements.get("system_send_routes", True)
