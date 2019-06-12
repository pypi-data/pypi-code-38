from abc import ABC, abstractmethod
from typing import Callable, Any, Generic, List

from rx import Observable
from rx.concurrency import NewThreadScheduler
from rx.disposable import Disposable

from treelab.grpc_treelab.messages.service_pb2 import EventPayload
from treelab.consts import *


class Listener(ABC, Generic[GenericType.T]):
    __slots__ = ('_name', '_disposable', '_thread_num', 'listenable_list')

    def __init__(self, name: str):
        """

        :param name:
        """
        self._name = name
        self._disposable: Disposable = None
        self._thread_num: int = 0
        self.listenable_list: List[GenericType.T] = []

    @abstractmethod
    def run(self, event: EventPayload):
        """
        Processing event, this is where the listener takes effect
        :param event:
        :return:
        """
        pass

    @property
    def name(self):
        return self._name

    @property
    def thread_num(self):
        return self._thread_num

    def subscribe_on(self, observable: Observable):
        """
        Subscribe on an observable sequence, an observable created from grpc stream, in this context
        :param observable:
        :return:
        """

        def subscription_func(event: EventPayload):
            self.run(event)

        self._disposable = observable.subscribe(subscription_func, scheduler=NewThreadScheduler())

    def dispose(self):
        """
        Stop listening
        :return:
        """
        if self._disposable and not self._disposable.is_disposed:
            self._disposable.dispose()

    def __repr__(self):
        return 'Listener.{}'.format(self.name)


class FunctionListener(Listener, ABC):
    def __init__(self, func: Callable[[EventPayload], Any], name: str):
        """

        :param func:
        :param name:
        """
        Listener.__init__(self, name)
        self.func = func

    def run(self, event):
        self.func(event)

