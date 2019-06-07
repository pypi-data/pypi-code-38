from prometheus_client import start_http_server, Histogram, Gauge
import time
import logging
import hemApp
import re

class instance(hemApp.Metrics):
    port = 8000
    cache = {}

    def __init__(self, config):
        self.port = config.get('port',8000)
        start_http_server(self.port)
        self.logger = logging.getLogger(__name__)
    def clean_name(name):
        return re.sub(r"[-\.]", "_", name)
    def stage(self, name, value):
        if 'result' in name:
            if name not in self.cache:
                self.cache[name] = Gauge(name.replace('.','_'), name)
            self.cache[name].set(value)
        else:
            if name not in self.cache:
                self.cache[name] = Histogram(name.replace('.','_'), name)
            self.cache[name].observe(value)

    def store(self):
        pass
    
