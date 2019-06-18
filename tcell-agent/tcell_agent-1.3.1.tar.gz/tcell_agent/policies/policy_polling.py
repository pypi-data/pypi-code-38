import os
import threading

from tcell_agent.tcell_logger import get_module_logger


def call_update(native_agent, policies_manager):
    result = native_agent.request_policies()
    policies_and_enablements = result.get("new_policies_and_enablements", {})
    policies_manager.process_policies(policies_and_enablements.get("enablements"),
                                      policies_and_enablements.get("policies"))


def run_polling_thread(native_agent, policies_manager):
    get_module_logger(__name__).info("Starting policy polling")
    while True:
        call_update(native_agent, policies_manager)


class PolicyPolling(object):
    def __init__(self, policies_manager, configuration):
        self.app_id = configuration.app_id
        self.api_key = configuration.api_key
        self.tcell_api_url = configuration.tcell_api_url
        self.fetch_policies_from_tcell = configuration.fetch_policies_from_tcell
        self.policies_manager = policies_manager

        self.polling_thread = None
        self.polling_thread_pid = os.getpid()

    def ensure_polling_thread_running(self, native_agent):
        if not (self.tcell_api_url and self.app_id and self.api_key):
            return

        if (not self.fetch_policies_from_tcell) or self.is_polling_thread_running():
            return

        self.start_polling_thread(native_agent)

    def is_polling_thread_running(self):
        return self.polling_thread and self.polling_thread.isAlive() and self.polling_thread_pid == os.getpid()

    def start_polling_thread(self, native_agent):
        self.polling_thread = threading.Thread(target=run_polling_thread,
                                               args=(native_agent, self.policies_manager,))
        self.polling_thread.daemon = True
        self.polling_thread.start()
        self.polling_thread_pid = os.getpid()
        get_module_logger(__name__).info("Starting the policy-polling thread")
