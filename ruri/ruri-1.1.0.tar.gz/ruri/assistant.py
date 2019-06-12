# ©2018 - Tim van Leuverden <TvanLeuverden@Gmail.com>
import colorama
import datetime
import logging
import sys
from progressbar import Percentage, Bar, AdaptiveETA, AdaptiveTransferSpeed
from timeit import default_timer as timer


class Assistant(object):
    CLEAN_LINE = "\033[F\033[0K"
    WIDGETS = [
        Percentage(), " ",
        Bar(), " ",
        AdaptiveETA(), " ",
        AdaptiveTransferSpeed()
    ]
    logger = logging.getLogger("ruri")

    def __init__(self, quiet_mode):
        self.start = timer()
        self.successful = 0
        self.not_found = 0
        self.no_match = 0
        self.failed = 0
        self.quiet_mode = quiet_mode

    @staticmethod
    def text_base(color, text):
        return "%s%s%s" % (color, text, colorama.Fore.RESET)

    def text_default(self, text):
        return self.text_base(colorama.Fore.RESET, text)

    def text_red(self, text):
        return self.text_base(colorama.Fore.RED, text)

    def text_green(self, text):
        return self.text_base(colorama.Fore.GREEN, text)

    def text_yellow(self, text):
        return self.text_base(colorama.Fore.YELLOW, text)

    def text_blue(self, text):
        return self.text_base(colorama.Fore.BLUE, text)

    def text_purple(self, text):
        return self.text_base(colorama.Fore.MAGENTA, text)

    def print_end(self, exit_code):
        end = timer()
        time = end - self.start
        time_str = str(datetime.timedelta(seconds=time))

        str_length = max(
            1,
            len(str(self.successful)),
            len(str(self.not_found)),
            len(str(self.no_match)),
            len(str(self.failed))
        )

        self.logger.info(
            "%s  %s  %s  %s  %s" % (
                self.text_green("✔ " + str(self.successful).rjust(str_length, '0')),
                self.text_yellow("⁉ " + str(self.not_found).rjust(str_length, '0')),
                self.text_red("✖ " + str(self.no_match).rjust(str_length, '0')),
                self.text_purple("‼ " + str(self.failed).rjust(str_length, '0')),
                self.text_blue("⏲ " + time_str)
            )
        )
        sys.exit(exit_code)
