try:
    from cStringIO import StringIO as WrappedStringIO
except ImportError:
    try:
        from StringIO import StringIO as WrappedStringIO
    except ImportError:
        from io import StringIO as WrappedStringIO

class StringIO(object):
    def __init__(self, stringio = None):
        self.encoding = None
        self.stringio_object = stringio
        if self.stringio_object is None:
            self.stringio_object = WrappedStringIO()
    
    def close (self):
        return self.stringio_object.close()

    def closed(self, x):
        return self.stringio_object.closed(x)

    def flush(self):
        return self.stringio_object.flush()
    
    def getvalue(self, use_pos=None):
        return self.stringio_object.getvalue(use_pos)

    def isatty(self):
        return self.stringio_object.isatty()

    def __next__(self):
        return next(self.stringio_object)

    def next(self):
        return self.stringio_object.next()

    def read(self, s=None):
        return self.stringio_object.read(s)

    def readline(self):
        return self.stringio_object.readline()

    def readlines(self):
        return self.stringio_object.readlines()

    def reset(self):
        return self.stringio_object.reset()

    def seek(self, position):
        return self.stringio_object.seek(position)

    def softspace(self, x, base = None):
        return self.stringio_object.softspace(x, base)

    def tell(self):
        return self.stringio_object.tell()

    def truncate(self):
        return self.stringio_object.truncate()

    def write(self, s):
        return self.stringio_object.write(s)

    def writelines(self, sequence_of_strings):
        return self.stringio_object.writelines(sequence_of_strings)
