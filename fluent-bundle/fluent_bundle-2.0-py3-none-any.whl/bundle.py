import inject
import applauncher.kernel
from applauncher.kernel import InjectorReadyEvent, ConfigurationReadyEvent
from fluent import handler, sender
import json


class FluentBundle(object):
    def __init__(self):
        self.log_handlers = []
        self.config_mapping = {
            "fluent": {
                "host": "localhost",
                "port": 24224,
                "tag": "app",
                "log_handler": {
                    "enabled": False,
                    "format": "{ " +
                            "'host': '%(hostname)s'," +
                            "'where': '%(module)s.%(funcName)s'," +
                            "'type': '%(levelname)s'," +
                            "'stack_trace': '%(exc_text)s'" +
                            "}"
                }
            }
        }
                
        self.event_listeners = [
            (InjectorReadyEvent, self.configure_logger),
            (ConfigurationReadyEvent, self.config_ready)
        ]

        self.injection_bindings = {}
        
    def config_ready(self, event):
        config = event.configuration.fluent

        self.injection_bindings[sender.FluentSender] = sender.FluentSender(config.tag, host=config.host, port=config.port)
        
    def configure_logger(self, event):
        config = inject.instance(applauncher.kernel.Configuration)
        logger_config = config.fluent.log_handler
        if logger_config.enabled:
            h = handler.FluentHandler(config.fluent.tag, host=logger_config.host, port=logger_config.port)
            formatter = handler.FluentRecordFormatter(json.loads(logger_config.format.replace("'", '"')))
            h.setFormatter(formatter)
            self.log_handlers.append(h)

