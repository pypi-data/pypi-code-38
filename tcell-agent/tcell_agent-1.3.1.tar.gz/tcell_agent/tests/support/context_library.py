from tcell_agent.config.configuration import set_config


class ConfigContext(object):

    def __init__(self, config):
        self.config = config

    def __enter__(self):
        set_config(self.config)

    def __exit__(self, *args):
        set_config(None)
