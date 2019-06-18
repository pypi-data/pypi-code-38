from invoke import Config, Context
from odoo_manager.core import paths as path_helpers


class BaseCommand(object):
    def __init__(self, options, depends_on_project=True, *args, **kwargs):
        self.options = options
        self.supported_commands = ()
        self.args = args
        self.kwargs = kwargs
        self.ctx = Context(Config())
        self.paths = None
        if depends_on_project:
            self.paths = path_helpers.Paths()

    def get_paths(self):
        if not self.paths:
            self.paths = path_helpers.Paths()
        return self.paths

    def run(self):
        """
        Implements general functionality for the run command. Adds support for
        subcommand via the `supported_commands` tuple.

        Each command class should call super when inheriting the run method.

        ```
        class MyCommand(BaseCommand):
            def run(self):
                subcommand = super(MyCommand, self).run()
                if not subcommand:
                    pass  # Perform some logic
        ```

        :return {NoneType}:
        """
        if not self.supported_commands:
            raise NotImplementedError("All commands must implement the run() method.")

        for command in self.supported_commands:
            if command in self.options and self.options[command]:
                method = "run_{}".format(command)
                if not hasattr(self, method):
                    raise NotImplementedError("The function {} has not been implemented yet.".format(method))
                getattr(self, method)()
                return method

        return None
