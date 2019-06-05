from swimlane_platform.lib.logger import SplitStreamLogger
from swimlane_platform.lib.args_config_questions import Configuration
from swimlane_platform.lib.names import names


class BaseWithLog(object):

    def __init__(self, args):
        # type: (Configuration) -> None
        self.args = args
        verbose = args.verbose if args.verbose else 0
        name = self.__class__.__name__ if self.__class__ else names.APP_NAME
        self.logger = SplitStreamLogger(name, verbose, args.log)
