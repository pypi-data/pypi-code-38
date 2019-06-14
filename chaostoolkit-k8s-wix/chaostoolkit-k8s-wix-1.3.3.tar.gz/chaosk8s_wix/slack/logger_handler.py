from logging import StreamHandler
from chaosk8s_wix.slack.client import post_message
import logging
import logzero

loger_initialized = False


class SlackHanlder(StreamHandler):
    def __init__(self):
        StreamHandler.__init__(self)

    def attach(self, logger):
        global loger_initialized
        if not loger_initialized:
            slack_handler = SlackHanlder()
            slack_handler.setLevel(logging.WARNING)
            slack_handler.setFormatter(logzero.LogFormatter(color=False))
            logger.addHandler(slack_handler)

            loger_initialized = True

    def emit(self, record):
        msg = self.format(record)
        post_message(msg)

        # print(">>", msg)
