from __future__ import unicode_literals

from tcell_agent.events.base_event import SensorEvent


class ServerAgentFrameworkEvent(SensorEvent):
    def __init__(self, framework, framework_version):
        super(ServerAgentFrameworkEvent, self).__init__("server_agent_details")
        self["app_framework"] = framework
        self["app_framework_version"] = framework_version
