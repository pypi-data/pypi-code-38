import time
import logging
import hemApp
class instance(hemApp.Metrics):
    config = None
    server = None
    port = 2003
    cache = []

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def stage(self, name, value):
        print("Stage: {} => {}".format(name, value))

    def store(self):
        print("  store")

    def __del__(self):
        self.store()