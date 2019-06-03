# -*- coding: utf-8 -*-
#
# from project CircuitBreaker : https://github.com/fabfuel/circuitbreaker
# with minimal adjustments
#
from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from functools import wraps
from datetime import datetime, timedelta
from typing import AnyStr, Iterable

import logging
import threading
import uuid
from halo_flask.exceptions import ApiError
from halo_flask.classes import AbsBaseClass

logger = logging.getLogger(__name__)

#manage monitor in a multi thread env
sem = threading.Semaphore()


STATE_CLOSED = 'closed'
STATE_OPEN = 'open'
STATE_HALF_OPEN = 'half_open'


class CircuitBreaker(AbsBaseClass):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 30
    EXPECTED_EXCEPTION = Exception

    def __init__(self,
                 failure_threshold=None,
                 recovery_timeout=None,
                 expected_exception=None,
                 name=None):
        self._failure_count = 0
        self._failure_threshold = failure_threshold or self.FAILURE_THRESHOLD
        self._recovery_timeout = recovery_timeout or self.RECOVERY_TIMEOUT
        self._expected_exception = expected_exception or self.EXPECTED_EXCEPTION
        self._name = name
        self._state = STATE_CLOSED
        self._opened = datetime.utcnow()
        self._uuid = str(uuid.uuid4())

    def __call__(self, wrapped):
        return self.decorate(wrapped)

    def decorate(self, function):
        """
        Applies the circuit breaker to a function
        """
        if self._name is None:
            self._name = function.__name__

        #CircuitBreakerMonitor.register(self)

        @wraps(function)
        def wrapper(*args, **kwargs):
            return self.call(function, *args, **kwargs)

        return wrapper

    def call(self, func, *args, **kwargs):
        """
        Calls the decorated function and applies the circuit breaker
        rules on success or failure
        :param func: Decorated function
        """
        CircuitBreakerMonitor.register(self)

        if self.opened:
            raise CircuitBreakerError(self)
        try:
            result = func(*args, **kwargs)
        except self._expected_exception:
            self.__call_failed()
            raise

        self.__call_succeeded()
        return result

    def __call_succeeded(self):
        """
        Close circuit after successful execution and reset failure count
        """
        self._state = STATE_CLOSED
        self._failure_count = 0
        logger.info("call_succeeded-Close circuit " + str(self.name)+ " : "+self._uuid)

    def __call_failed(self):
        """
        Count failure and open circuit, if threshold has been reached
        """
        self._failure_count += 1
        if self._failure_count >= self._failure_threshold:
            self._state = STATE_OPEN
            self._opened = datetime.utcnow()
            logger.debug("call_failed-Open circuit " + str(self.name)+ " : "+self._uuid)

    @property
    def state(self):
        if self._state == STATE_OPEN and self.open_remaining <= 0:
            return STATE_HALF_OPEN
        return self._state

    @property
    def open_until(self):
        """
        The datetime, when the circuit breaker will try to recover
        :return: datetime
        """
        return self._opened + timedelta(seconds=self._recovery_timeout)

    @property
    def open_remaining(self):
        """
        Number of seconds remaining, the circuit breaker stays in OPEN state
        :return: int
        """
        return (self.open_until - datetime.utcnow()).total_seconds()

    @property
    def failure_count(self):
        return self._failure_count

    @property
    def closed(self):
        return self.state == STATE_CLOSED

    @property
    def opened(self):
        return self.state == STATE_OPEN

    @property
    def name(self):
        return self._name

    def __str__(self, *args, **kwargs):
        return self._name


class CircuitBreakerError(ApiError):
    def __init__(self, circuit_breaker, *args, **kwargs):
        """
        :param circuit_breaker:
        :param args:
        :param kwargs:
        :return:
        """
        super(CircuitBreakerError, self).__init__("msg",*args, **kwargs)
        self._circuit_breaker = circuit_breaker

    def __str__(self, *args, **kwargs):
        return 'Circuit "%s" OPEN until %s (%d failures, %d sec remaining)' % (
            self._circuit_breaker.name,
            self._circuit_breaker.open_until,
            self._circuit_breaker.failure_count,
            round(self._circuit_breaker.open_remaining)
        )


class CircuitBreakerMonitor(AbsBaseClass):
    circuit_breakers = {}

    @classmethod
    def register(cls, circuit_breaker):
        if circuit_breaker.name not in cls.circuit_breakers:
            sem.acquire()
            cls.circuit_breakers[circuit_breaker.name] = circuit_breaker
            sem.release()

    @classmethod
    def all_closed(cls):
        # type: () -> bool
        return len(list(cls.get_open())) == 0

    @classmethod
    def get_circuits(cls):
        # type: () -> Iterable[CircuitBreaker]
        return cls.circuit_breakers.values()

    @classmethod
    def get(cls, name):
        # type: (AnyStr) -> CircuitBreaker
        return cls.circuit_breakers.get(name)

    @classmethod
    def get_open(cls):
        # type: () -> Iterable[CircuitBreaker]
        for circuit in cls.get_circuits():
            if circuit.opened:
                yield circuit

    @classmethod
    def get_closed(cls):
        # type: () -> Iterable[CircuitBreaker]
        for circuit in cls.get_circuits():
            if circuit.closed:
                yield circuit


def circuit(failure_threshold=None,
            recovery_timeout=None,
            expected_exception=None,
            name=None,
            cls=CircuitBreaker):

    # if the decorator is used without parameters, the
    # wrapped function is provided as first argument
    if callable(failure_threshold):
        return cls().decorate(failure_threshold)
    else:
        return cls(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception,
            name=name)
