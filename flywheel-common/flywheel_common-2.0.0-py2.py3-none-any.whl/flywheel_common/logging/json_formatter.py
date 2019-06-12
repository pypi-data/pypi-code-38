import datetime
import json
import logging
import os


class JSONLogFormatter(logging.Formatter):

    def __init__(self, tag=None):
        self.tag = tag
        super(JSONLogFormatter, self).__init__()

    def format(self, record):
        # Start with context values, and overwrite with fixed values
        record_dictionary = getattr(record, 'context', {})
        record_dictionary.update({
            'message': record.getMessage(),
            'severity': record.levelname,
            'timestamp': str(datetime.datetime.fromtimestamp(float(record.created))),
            'process': record.process,
            'filename': os.path.basename(record.pathname),
            'lineno': record.lineno,
            'thread': record.thread,
        })

        if record.exc_info:
            record_dictionary['exc_info'] = self.formatException(record.exc_info)

        formatted_record = json.dumps(record_dictionary)
        return '{}: {}'.format(self.tag, formatted_record) if self.tag else formatted_record
