class LazyString(object):
    def __init__(self, formatstring, *args, **kwargs):
        self.formatstring = formatstring
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.formatstring.format(*self.args, **self.kwargs)

    def __repr__(self):
        return 'LazyString({!r}, args={!r}, kwargs={!r})'.format(
            self.formatstring,
            self.args,
            self.kwargs)
