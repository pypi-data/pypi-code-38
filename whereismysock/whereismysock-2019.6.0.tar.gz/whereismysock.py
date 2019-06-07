"""
A convenient way to work with information streaming from websockets, built on
top of the Python iterator protocol and the excellent lomond library.
"""

import threading
from collections import deque
from collections.abc import Iterator

import lomond


def latest(websocket):
    """
    Given a websocket, returns one each iteration the latest message received,
    None if no value has been received yet.
    """
    return Stream(websocket, PopOrLatest)


def most(websocket, keep=1000):
    """
    Given a websocket, returns a list of the latest `keep` messages received
    between two iterations, [] if no new messages were received.
    """
    return Stream(websocket, AllSinceLast, maxlen=keep)


def all(websocket):
    """
    Given a websocket, returns a list of at the messages received between two
    iterations, [] if no new messages were received.
    """
    return Stream(websocket, AllSinceLast, maxlen=None)


class Stream(Iterator):
    """
    Given a websocket, a Get class and maxlen (default to 1), starts a thread
    listening to incoming data from the websocket which are pushed in a queue
    used by an instance of Get called in the next method. Iterators for the win!
    """

    def __init__(self, websocket, Get, maxlen=1):
        self.queue = deque(maxlen=maxlen)
        self.listener = Listener(websocket, self.queue)
        self.listener.start()
        self.get = Get(self.queue)

    def __next__(self):
        if not self.listener.is_alive():
            raise LostASock("check the dryer!")
        return self.get()


class Listener(threading.Thread):
    """
    Given a websocket and a queue, instance is a thread which when started will
    append all messages received from the websocket to the queue.
    """

    def __init__(self, websocket, queue):
        self.websocket = websocket
        self.queue = queue
        super().__init__()
        self.daemon = True

    def run(self):
        self.connection = lomond.WebSocket(self.websocket)
        for event in self.connection:
            if event.name == "text":
                self.queue.append(event.text)


class PopOrLatest:
    """
    Given a queue (had a pop method), instance is a callable which returns
    the popped value or the last popped value (None by default).
    """

    def __init__(self, queue):
        self.queue = queue
        self.latest = None

    def __call__(self):
        try:
            self.latest = self.queue.pop()
        except IndexError:
            pass
        return self.latest


class AllSinceLast:
    """
    Given a queue (has a popleft method), instance is a callable which returns
    a list of all the values added to the queue since it was last called.
    """

    def __init__(self, queue):
        self.queue = queue

    def __call__(self):
        result = []
        try:
            while True:
                result.append(self.queue.popleft())
        except IndexError:
            pass
        return result


class LostASock(Exception):
    pass
