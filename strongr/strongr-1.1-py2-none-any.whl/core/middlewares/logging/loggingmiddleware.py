from cmndr import Middleware

import logging

class LoggingMiddleware(Middleware):

    def execute(self, command, next_callable):
        cmd_dict = command.__dict__

        splitted_module = command.__module__.split('.')
        domain = splitted_module[1]
        log_string = '{} {}'.format(' '.join(splitted_module[-2:]), cmd_dict if cmd_dict else '')
        logging.getLogger(domain).info(log_string)
        ret = next_callable(command)
        return ret
