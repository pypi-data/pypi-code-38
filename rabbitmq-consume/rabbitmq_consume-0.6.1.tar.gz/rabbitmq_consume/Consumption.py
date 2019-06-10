#!/usr/bin/env python

class StopWorkerException(Exception):
    def __init__(self, message = None):
        if None != message:
            super(StopWorkerException, self).__init__(message)


class StopListeningException(Exception):
    def __init__(self, message = None):
        if None != message:
            super(StopListeningException, self).__init__(message)


import abc

class Consumption():

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 properties,
                 body,
                 redelivered):
        pass

    @abc.abstractmethod
    def consume(self):
        pass
