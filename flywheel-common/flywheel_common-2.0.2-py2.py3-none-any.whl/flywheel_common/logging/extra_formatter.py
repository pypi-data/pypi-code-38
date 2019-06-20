import logging

def wrap_default_handler(root):
    """Update the default root handler to log extras"""
    # No handlers, skip this step
    if not root.handlers:
        return

    # Prevent extra levels of wrapping
    if isinstance(root.handlers[0].formatter, ExtrasFormatterWrapper):
        return

    fmt = ExtrasFormatterWrapper(root.handlers[0].formatter)
    root.handlers[0].setFormatter(fmt)


class ExtrasFormatterWrapper(logging.Formatter):
    """Wraps formatter, printing extras to the output"""
    def __init__(self, formatter):
        super(ExtrasFormatterWrapper, self).__init__()
        self.formatter = formatter

    def format(self, record):
        # Format using the wrapped formatter (or delegate to super)
        if self.formatter is not None:
            s = self.formatter.format(record)
        else:
            s = super(ExtrasFormatterWrapper, self).format(record)

        # Add extras, if present on the record
        extra = getattr(record, 'context', None)
        if extra:
            for context_value in extra.items():
                s += ('; %s=%s' % context_value)

        return s
