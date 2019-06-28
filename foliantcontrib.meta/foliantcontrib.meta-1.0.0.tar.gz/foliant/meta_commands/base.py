from logging import Logger


class BaseMetaCommand:
    '''Base meta command.

    All meta commands extensions must inherit from this one.'''
    config_section = ''
    defaults = {}

    def __init__(self, context: dict, logger: Logger):
        self.context = context
        self.logger = logger
        self.config = context['config']
        self.project_path = context['project_path']
        options = self.config.get(self.config_section, {}) if self.config_section else {}
        self.options = {**self.defaults, **options}

    def run(self, *args, **kwargs):
        raise NotImplementedError()
