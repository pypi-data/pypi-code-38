import logging

from datetime import datetime

from tcell_agent.version import VERSION


class TCellLogFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%dT%H:%M:%S")
            s = "%s.%03d" % (t, record.msecs)

        return s

    def format(self, record):
        record.tcell_version = VERSION
        return super(TCellLogFormatter, self).format(record)
