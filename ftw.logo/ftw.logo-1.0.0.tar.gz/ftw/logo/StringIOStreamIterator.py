from ZPublisher.Iterators import IStreamIterator
from zope.interface import implementer
from StringIO import StringIO


@implementer(IStreamIterator)
class StringIOStreamIterator(StringIO):

    def __len__(self):
        return self.len
