#!/usr/bin/env python

from j5basic import WithContextSkip
import inspect
import logging
import threading
import sys

block_event_lock = threading.Lock()
block_events = {}

@WithContextSkip.conditionalcontextmanager
def only_thread(thread_name):
    """Runs the controlled block only if the current thread has the given name - otherwise skips it"""
    if thread_name == threading.current_thread().name:
        yield
    else:
        raise WithContextSkip.SkipStatement()

@WithContextSkip.conditionalcontextmanager
def only_thread_blocking(thread_name, block_name=None):
    """Runs the controlled block only if the current thread has the given name - otherwise skips it. Wait for the given thread to run the block before allowing other threads to proceed"""
    with block_event_lock:
        if block_name is None:
            frame = sys._getframe().f_back.f_back
            filename = frame.f_code.co_filename
            if filename.startswith("<"):
                filename = filename + "/0x%x" % id(frame.f_code)
            block_name = "%s:%d" % (filename, frame.f_lineno)
        block_event = block_events.setdefault(block_name, threading.Event())
    current_thread_name = threading.current_thread().name
    if thread_name == current_thread_name:
        logging.info("thread %s will run %s", thread_name, block_name)
        yield
        logging.info("thread %s ran %s", thread_name, block_name)
        block_event.set()
        logging.info("thread %s has set event %s", thread_name, block_name)
    else:
        logging.info("thread %s will wait for event %s", thread_name, block_name)
        block_event.wait()
        logging.info("thread %s has received event %s and will skip the block", thread_name, block_name)
        raise WithContextSkip.SkipStatement()

