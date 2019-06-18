import json
import os

from stackifyapm.base import Client
from stackifyapm.conf import setup_logging
from stackifyapm.instrumentation.control import instrument


def make_client(**defaults):
    config_file = defaults.get("CONFIG_FILE") or defaults.get("config_file") or 'stackify.json'
    application_name = defaults.get("APPLICATION_NAME") or defaults.get("application_name") or 'Python Application'
    environment = defaults.get("ENVIRONMENT") or defaults.get("environment") or 'Production'
    base_dir = defaults.get("BASE_DIR") or defaults.get("base_dir") or os.getcwd()

    try:
        with open(config_file) as json_file:
            data = json.load(json_file)
            application_name = data.get('application_name') or application_name
            environment = data.get('environment') or environment
            base_dir = data.get('base_dir') or base_dir
    except Exception:
        pass

    config = {
        "APPLICATION_NAME": application_name,
        "ENVIRONMENT": environment,
        "BASE_DIR": base_dir,
        "CONFIG_FILE": config_file,
    }

    return Client(config, **defaults)


class StackifyAPM(object):
    """
    Generic application for StackifyAPM.
    """
    def __init__(self, **defaults):
        self.client = make_client(**defaults)
        setup_logging(self.client)
        instrument(self.client)
