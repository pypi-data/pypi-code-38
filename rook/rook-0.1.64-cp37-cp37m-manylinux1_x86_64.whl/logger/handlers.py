import json
import logging
from logging.handlers import RotatingFileHandler

from six import iteritems


class RookoutLogHandler(logging.Handler):

    @staticmethod
    def update_record(record):
        # Enable override of basic log elements
        def update_from_override(original_name, update_name):
            update_data = getattr(record, update_name, None)
            if update_data is not None:
                setattr(record, original_name, update_data)

        updates = {"_module": "module",
                   "_funcName": "funcName",
                   "_lineno": "lineno"}

        for update, original in iteritems(updates):
            update_from_override(original, update)
        rookout_args = ""
        if hasattr(record, "rookout_extra"):
            rookout_args = json.dumps(getattr(record, "rookout_extra"))
        setattr(record, "rookout_extra", rookout_args)
        return record

    def emit(self, record):
        record = self.update_record(record)
        # Pass to actual emit
        super(RookoutLogHandler, self).emit(record)


class RookoutStreamHandler(RookoutLogHandler, logging.StreamHandler):
    pass


class RookoutFileHandler(RookoutLogHandler, RotatingFileHandler):
    pass
