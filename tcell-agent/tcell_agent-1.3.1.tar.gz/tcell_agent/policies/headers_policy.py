from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class HeadersPolicy(TCellPolicy):
    api_identifier = "headers"

    def __init__(self, native_agent, enablements, _):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.headers_enabled = False
        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.headers_enabled = enablements.get("headers", False)

    def get_headers(self, tcell_context):
        if not self.headers_enabled:
            return []

        whisper = self.native_agent.get_headers(tcell_context)
        return whisper.get("headers") or []
