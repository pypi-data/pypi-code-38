from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class JsAgentPolicy(TCellPolicy):
    api_identifier = "jsagentinjection"

    def __init__(self, native_agent, enablements, _):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.jsagent_enabled = False
        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.jsagent_enabled = enablements.get("jsagentinjection", False)

    def get_js_agent_script_tag(self, tcell_context):
        if not self.jsagent_enabled:
            return None

        whisper = self.native_agent.get_js_agent_script_tag(tcell_context)
        return whisper.get("script_tag")
