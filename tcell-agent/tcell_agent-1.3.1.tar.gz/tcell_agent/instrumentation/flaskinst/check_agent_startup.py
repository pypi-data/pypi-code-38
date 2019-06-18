from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.events.server_agent_framework_event import ServerAgentFrameworkEvent


@catches_generic_exception(__name__, "Error starting agent")
def start_agent():
    TCellAgent.startup()

    from tcell_agent.instrumentation.flaskinst.routes import report_routes
    report_routes()

    from flask import __version__
    sade = ServerAgentFrameworkEvent("Flask", __version__)
    TCellAgent.send(sade)
