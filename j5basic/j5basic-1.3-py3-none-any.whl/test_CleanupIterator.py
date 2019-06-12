#!/usr/bin/env python

from j5basic import CleanupIterator
from j5test.Utils import raises
import six

class TestCleanupIterator:
    def test_simple_call(self):
        """tests that a cleanup generator runs through an iterator and calls the cleanup at the end"""
        i = iter([1,2,3,4,5])
        def cleanup():
            assert raises(StopIteration, lambda: six.next(i))
            cleanup.cleanup_called = True
        cleanup.cleanup_called = False
        g = CleanupIterator.CleanupIterator(i, cleanup)
        l = list(g)
        assert l == [1,2,3,4,5]
        assert cleanup.cleanup_called
        assert raises(StopIteration, lambda: six.next(i))

    def test_empty_call(self):
        """tests that a cleanup generator runs through an empty iterator and calls the cleanup at the end"""
        i = iter([])
        def cleanup():
            assert raises(StopIteration, lambda: six.next(i))
            cleanup.cleanup_called = True
        cleanup.cleanup_called = False
        g = CleanupIterator.CleanupIterator(i, cleanup)
        l = list(g)
        assert l == []
        assert cleanup.cleanup_called
        assert raises(StopIteration, lambda: six.next(i))

    def test_args_call(self):
        """tests that a cleanup generator runs through an iterator and passes arguments successfully"""
        i = iter([1,2,3,4,5])
        def cleanup(*args, **kwargs):
            cleanup.cleanup_args = args
            cleanup.cleanup_kwargs = kwargs
        g = CleanupIterator.CleanupIterator(i, cleanup, 1,2,3, fred="president")
        l = list(g)
        assert l == [1,2,3,4,5]
        assert cleanup.cleanup_args == (1,2,3)
        assert cleanup.cleanup_kwargs == {"fred": "president"}

    def test_error_call(self):
        """tests that a cleanup generator catches exceptions raised by an iterator and cleans up afterwards"""
        class MyFailingIterator(object):
            def __init__(self):
                self.n = 0
            def __iter__(self):
                return self
            def __next__(self):
                self.n += 1
                if self.n == 3:
                    raise ValueError("self.n is %s" % self.n)
                return self.n
            def next(self):
                return self.__next__()
        i = MyFailingIterator()
        def cleanup():
            cleanup.cleanup_called = True
        cleanup.cleanup_called = False
        g = CleanupIterator.CleanupIterator(i, cleanup)
        def receive(g):
            receive.result = []
            for item in g:
                receive.result.append(item)
        assert raises(ValueError, receive, g)
        assert cleanup.cleanup_called
        assert receive.result == [1, 2]
        # make sure that we do not allow the iterator to continue after an exception has been raised
        assert raises(StopIteration, g.__next__)

