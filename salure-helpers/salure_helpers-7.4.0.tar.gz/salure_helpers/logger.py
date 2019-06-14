import logging
import os


class Logger:
    def __init__(self, customer, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        if not os.path.isdir('/var/log/scheduler/{}'.format(customer)):
            os.mkdir('/var/log/scheduler/{}'.format(customer))
        handler = logging.FileHandler('/var/log/scheduler/{}/{}.log'.format(customer, logger_name))
        handler.setFormatter(logging.Formatter('%(levelname)s | %(asctime)s|%(name)s | LineNo:%(lineno)s |%(message)s'))
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)