# coding: utf-8

from deployv.messaging.basemsg import BaseWorker
from deployv.base import errors
import logging


_logger = logging.getLogger('deployv')


class HttpWorker(BaseWorker):
    def __init__(self, configuration_object, sender_class, receiver_class,
                 worker_id):
        super(HttpWorker, self).__init__(configuration_object, sender_class, receiver_class,
                                         worker_id)

    def run(self):
        """ Worker method, runs the method that performs a request to the odoo controller
        and retrieves the messages
        """
        _logger.info("Worker %s - waiting for something to do", self._wid)
        try:
            self._receiver.run(self.callback)
        except errors.GracefulExit:
            # Catch the exception raised in the threads when they are being stopped
            pass

    def signal_exit(self):
        """ Exit when finished with current loop """
        self._receiver.stop()

    def kill(self):
        """ This kill immediately the process, should not be used """
        self._receiver.stop()
        self.terminate()
        self.join()

    def callback(self, body):
        message = self.check_message(body)
        if message:
            _logger.info('Received a message worker %s', self._wid)
            self.execute_rpc(message)
