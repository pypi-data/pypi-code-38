from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class CommandInjectionPolicy(TCellPolicy):
    api_identifier = "cmdi"

    def __init__(self, native_agent, enablements, _):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.cmdi_enabled = False

        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.cmdi_enabled = enablements.get("cmdi", False)

    # Note: this is a dangerous call if it runs too early in the
    #       agent startup process. Currently it works fine based
    #       on the PlaceholderNativeAgent.
    #
    #       This scenario should be taken into consideration if
    #       this is changed in the future:

    #       cmdi events are special because they can be triggered very
    #       easily by running any shell command startup scripts are likely
    #       to run shell commands. it's not a good idea to startup the event
    #       processor before worker processses are forked, so the safest
    #       thing to do is let a different event start the event processor
    #       to avoid deadlocking worker processes. more details:
    #       https://github.com/tcellio/pythonagent-tcell/pull/221
    def block_command(self, cmd, tcell_context):
        if not self.cmdi_enabled:
            return False

        return self.native_agent.apply_cmdi(
            cmd, tcell_context
        ).get("blocked", False)
