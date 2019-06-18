from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class PatchesPolicy(TCellPolicy):
    api_identifier = "patches"

    def __init__(self, native_agent, enablements, _):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.patches_enabled = False
        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.patches_enabled = enablements.get("patches", False)

    def block_request(self, appsensor_meta):
        if not self.patches_enabled:
            return False

        whisper = self.native_agent.apply_patches(appsensor_meta)
        if whisper.get("apply_response"):
            response = whisper["apply_response"]
            return response.get("status") == "Blocked"

        return False
