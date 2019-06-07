import logging
from .notification import Notification


class LogNotification(Notification):
    """Logs via log_cfg, and also to a notification file with the format '[date time][self.name] msg'"""

    def __init__(self, name, log_file):
        super().__init__(name)
        handler = logging.FileHandler(filename=log_file, mode='a')
        handler.setFormatter(
            logging.Formatter(
                fmt='[%(asctime)s][' + self.name + '] %(message)s',
                datefmt='%Y-%b-%d %H:%M:%S'
            )
        )
        handler.setLevel(logging.INFO)
        self._logger.addHandler(handler)

    def notify(self, msg, attachments=None):
        self.info(msg)
        if attachments:
            if isinstance(attachments, str):
                attachments = [attachments]

        for attachment in attachments or []:
            self.info('Attachment: %s', attachment)
