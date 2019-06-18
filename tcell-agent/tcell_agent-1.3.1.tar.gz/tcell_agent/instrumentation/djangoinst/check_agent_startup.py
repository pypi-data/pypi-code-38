import threading

from django import get_version
from django.conf import settings

from tcell_agent.global_state import has_agent_started, set_agent_has_started, update_default_charset

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.settings import send_django_setting_events
from tcell_agent.events.server_agent_framework_event import ServerAgentFrameworkEvent


AGENT_STARTED_LOCK = threading.Lock()


def start_agent():
    with AGENT_STARTED_LOCK:
        # need to check state again after acquiring lock
        if has_agent_started():
            return False

        set_agent_has_started()
        TCellAgent.startup()

    return True


@catches_generic_exception(__name__, "Error checking agent startup")
def ensure_agent_started():
    if has_agent_started():
        return

    if settings.DEFAULT_CHARSET:
        update_default_charset(settings.DEFAULT_CHARSET)

    if start_agent():
        sade = ServerAgentFrameworkEvent("Django", get_version())
        TCellAgent.send(sade)
        send_django_setting_events()
