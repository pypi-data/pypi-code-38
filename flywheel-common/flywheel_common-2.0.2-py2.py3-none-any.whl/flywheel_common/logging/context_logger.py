import json
import collections
import logging

class LoggerContextAdapter(logging.LoggerAdapter):
    """Class that provides syntactic sugar for adding context to a log"""
    def __init__(self, logger, context=None):
        if context is None:
            context = collections.OrderedDict()
        self.context = context

        super(LoggerContextAdapter, self).__init__(logger, {'context': self.context})

    def with_context(self, **kwargs):
        """Create a new logger, setting the context attributes specified by kwargs

        Arguments:
            **kwargs: The key-value pairs to set as context
        Returns:
            LoggerContextAdapter: The new logger with context
        """
        context = self.context.copy()
        context.update(kwargs)
        return LoggerContextAdapter(self.logger, context)

    # ===== Methods not Overridden in python 2.7 =====
    def setLevel(self, level):
        """Set the specified level on the underlying logger."""
        self.logger.setLevel(level)

    def warn(self, msg, *args, **kwargs):
        """
        Delegate a warning call to the underlying logger, after adding
        contextual information from this adapter instance.
        """
        msg, kwargs = self.process(msg, kwargs)
        self.logger.warning(msg, *args, **kwargs)

def getContextLogger(name=None):
    """Get a LoggerAdapter that supports adding context.
    Arguments:
        name (str): The logger name
    """
    return LoggerContextAdapter(logging.getLogger(name))
