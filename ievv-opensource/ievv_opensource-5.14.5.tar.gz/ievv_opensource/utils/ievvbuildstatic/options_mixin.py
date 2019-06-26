class OptionsMixin(object):
    def get_option(self, key, fallback=None):
        return self.app.apps.options.get(key, fallback)

    def is_in_production_mode(self):
        return self.app.apps.is_in_production_mode()

    @classmethod
    def add_cli_arguments(cls, parser):
        """
        Add CLI arguments.

        The arguments are forwarder to __init__ via the


        Args:
            parser: argparse parser.
        """
