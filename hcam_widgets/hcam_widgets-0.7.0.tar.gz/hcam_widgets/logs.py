from __future__ import print_function, unicode_literals, absolute_import, division
import logging
import time
import six
import sys

from .tkutils import get_root
if not six.PY3:
    import Tkinter as tk
else:
    import tkinter as tk


class GuiHandler(logging.Handler):
    """
    This defines the output sent to a text widget GUI
    """
    def __init__(self, twidget):
        """
        twidget : text widget to display logging messages
        """
        logging.Handler.__init__(self)
        logging.Formatter.converter = time.gmtime
        formatter = logging.Formatter('%(asctime)s - %(message)s\n', '%H:%M:%S')
        self.setFormatter(formatter)

        # ignore DEBUG messages
        self.setLevel(logging.INFO)

        # configure and store the text widget
        g = get_root(twidget).globals
        twidget.tag_config('DEBUG', background=g.COL['debug'])
        twidget.tag_config('INFO')
        twidget.tag_config('WARNING', background=g.COL['warn'])
        twidget.tag_config('ERROR', background=g.COL['error'])
        twidget.tag_config('CRITICAL', background=g.COL['critical'])
        self.twidget = twidget

    def emit(self, message):
        formattedMessage = self.format(message)

        # Write message to twidget
        g = get_root(self.twidget).globals
        self.twidget.configure(state=tk.NORMAL, font=g.ENTRY_FONT)
        self.twidget.insert(tk.END, formattedMessage, (message.levelname,))

        # Prevent further input
        self.twidget.configure(state=tk.DISABLED)
        self.twidget.see(tk.END)


class FileHandler(logging.FileHandler):
    """
    Used to send logging output to a file
    """
    def __init__(self, fname):
        """
        fout: file pointer to send messages to
        """
        logging.FileHandler.__init__(self, fname)
        logging.Formatter.converter = time.gmtime
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-7s %(message)s',
                                      '%Y-%m-%d %H:%M:%S')
        self.setFormatter(formatter)

        # include DEBUG messages
        self.setLevel(logging.DEBUG)


class StreamHandler(logging.StreamHandler):
    """
    Used to send logging output to stderr
    """
    def __init__(self):
        """
        fout: file pointer to send messages to
        """
        logging.StreamHandler.__init__(self)
        logging.Formatter.converter = time.gmtime
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)-7s %(message)s\n',
                                      '%H:%M:%S')
        self.setFormatter(formatter)
        self.setLevel(logging.INFO)

    def emit(self, message):
        """
        Overwrites the default handler's emit method:

        message : the message to display
        """
        sys.stderr.write(self.format(message))


class Logger(object):
    """
    Defines an object for logging. This uses the logging module to
    define an internal logger and then defines how it reports to
    stderr and, optionally, a file. It also defines shortcuts to
    the standard logging methods warn, info etc. This is mainly
    as a base class for two GUI-based loggers that come next.

     logname : unique name for logger

    """

    def __init__(self, logname):

        # make a logger
        self._log = logging.getLogger(logname)

        # disable automatic logging to the terminal
        self._log.propagate = False

        # add terminal handler that avoids debug messages
        self._log.addHandler(StreamHandler())

    def update(self, fname):
        """
        Adds a handler to save to a file. Includes debug stuff.
        """
        ltfh = FileHandler(fname)
        self._log.addHandler(ltfh)

    def debug(self, message):
        self._log.debug(message)

    def info(self, message):
        self._log.info(message)

    def warn(self, message):
        self._log.warn(message)

    def error(self, message):
        self._log.error(message)

    def critical(self, message):
        self._log.critical(message)
