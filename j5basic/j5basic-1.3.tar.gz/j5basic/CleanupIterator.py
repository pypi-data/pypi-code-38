#!/usr/bin/env python

"""this is an iterator wrapper that allows things to be cleaned up when the end of the iterator is reached"""

class CleanupIterator(object):
    """this is an iterator wrapper that allows things to be cleaned up when the end of the iterator is reached or an error occurs"""
    def __init__(self, iterator, cleanup_call, *cleanup_args, **cleanup_kwargs):
        """Construct a cleanup generator over the given iterator that will call cleanup_call with the given args"""
        self.iterator = iterator
        self.cleanup_call = cleanup_call
        self.cleanup_args = cleanup_args
        self.cleanup_kwargs = cleanup_kwargs
        self.cleaned_up = False

    def __iter__(self):
        """Mark that we are our own iterator"""
        return self

    def __next__(self):
        """return the next result for the iterator, and call cleanup_call once the iterator stops, or if an error is raised"""
        if self.cleaned_up:
            # do not allow any more iteration once we have cleaned up
            # this is in case an iterator raises an error, we clean up, but the iterator is not finished
            # this class should only be used on iterators that stop if they raise an error, otherwise the cleanup point is indeterminable
            raise StopIteration()
        try:
            return next(self.iterator)
        except (Exception, StopIteration):
            self.cleaned_up = True
            # if a clean up error happens, it will be raised instead of the iterator error
            self.cleanup_call(*self.cleanup_args, **self.cleanup_kwargs)
            raise

    def next(self):
        return self.__next__()

