

class CommandRunner:
    """Sets up the environment to run QSA command from an interactive
    shell and executes them.
    """

    def __init__(self, config, injector):
        self.cfg = config
        self.injector = injector

    def run(self, func, args):
        func_args, func_kwargs = self.injector.resolve(func)
        func(*func_args, **func_kwargs)
