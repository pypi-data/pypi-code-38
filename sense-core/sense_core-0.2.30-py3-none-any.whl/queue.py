from .queue0 import *
from .log import log_exception, log_info, log_warn
from .utils import sleep
from pika.exceptions import *


class RabbitProducer(RabbitProducer0):

    def send_safely(self, topic, message, need_close=False):
        times = 1
        while times >= 0:
            try:
                times -= 1
                self.send(topic, message, need_close)
                return True
            except Exception as ex:
                log_warn("send message fir {0} failed ex:{1}".format(topic, str(ex)))
                self.close_safely()
                sleep(1)
        return False

    def close_safely(self):
        try:
            self.close_connection()
        except Exception as ex:
            log_exception(str(ex))


class RabbitConsumer(RabbitConsumer0):

    def _close_safely(self):
        try:
            self.close_connection()
        except Exception as ex:
            log_exception(str(ex))

    def execute_safely(self, caller, prefetch_count=2, no_ack=False):
        while True:
            try:
                self.execute(caller, prefetch_count,no_ack)
            except ConnectionClosed as ex:
                log_info("rabbit ConnectionClosed reset")
                self._close_safely()
                sleep(2)
            except ChannelClosed as ex:
                log_info("rabbit ChannelClosed reset")
                self._close_safely()
                sleep(2)
            except Exception as ex:
                log_exception(ex)
                self._close_safely()
                raise ex
