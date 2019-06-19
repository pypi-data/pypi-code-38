from typing import Dict

from rx import from_

from treelab.client import TreeLabClient
from treelab.event_handling.listener import *
from treelab.grpc_treelab.messages.service_pb2 import *
import time
from treelab.rxmq_treelab.rxmq import Rxmq
from treelab.utils.misc_utils import get_event_identifier


class EventHandler:
    __slots__ = ('token', 'subscription_input', '_registered_listeners',
                 'iterating_listener_dict', 'init_listener', 'iterating_listener')
    """
    Event handler for treelab, use register/deregister to control the listeners currently on treelab
    """

    def __init__(self, subscription_input: WorkspaceSubscriptionInput, token: str):
        """

        :param subscription_input:
        """
        self.token = token
        self.subscription_input: WorkspaceSubscriptionInput = subscription_input
        self._registered_listeners: Dict[str, Listener] = {}
        self._init_subscribe()
        self.iterating_listener_dict: Dict[int, Listener] = {}

    def register(self, listener: Listener):
        """
        Register a listener
        :param listener:
        :return:
        """
        self._registered_listeners[listener.name] = listener

    def _subscribe(self, listener: Listener):
        """
        subscribe to a listener
        :return:
        """
        grpc_stream = TreeLabClient(token=self.token).subscribe_to_workspace(self.subscription_input)
        grpc_stream_observable = from_(grpc_stream)

        listener.subscribe_on(grpc_stream_observable)

    def _subscribe_all(self):
        """
        Subscribing for all listeners in self.registered_listeners in a single thread,
        this will create a new listener called iterating_listener that will take actions iteratively on listeners
        registered in self.registered_listeners
        :return:
        """

        class _IteratingListener(Listener):
            def __init__(self, listeners: List[Listener], name: str):
                super().__init__(name)
                self.listeners = listeners

            def run(self, event):
                for listener in self.listeners:
                    listener.run(event)

        listeners_by_thread = self._group_listeners()
        for thread_num, listeners_on_thread in listeners_by_thread.items():
            iterating_listener = _IteratingListener(listeners_on_thread, 'iterating_listener_{}'.format(thread_num))
            self._subscribe(iterating_listener)
            self.iterating_listener_dict[thread_num] = iterating_listener

    def _group_listeners(self):
        listeners_by_thread = {}
        for listener in self.registered_listeners.values():
            if listener.thread_num not in listeners_by_thread:
                listeners_by_thread[listener.thread_num] = []
            listeners_by_thread[listener.thread_num].append(listener)
        return listeners_by_thread

    def _init_subscribe(self):
        class _InitListener(Listener):
            def __init__(self, subscription_input: WorkspaceSubscriptionInput, name: str):
                """

                :param subscription_input:
                :param name:
                """
                Listener.__init__(self, name)
                self.subscription_input = subscription_input
                self.last_event_time: float = time.time()

            def run(self, event: EventPayload):
                Rxmq.channel(self.subscription_input.workspaceId).subject(get_event_identifier(event))
                self.last_event_time = time.time()

        self.init_listener = _InitListener(subscription_input=self.subscription_input, name='init_subscription')
        self._subscribe(self.init_listener)

    def get_new_listener_name(self):
        """
        Helper function that generate a new listener name by the size of registered_listeners
        :return:
        """
        listener_name = 'listener_{}'.format(len(self.registered_listeners))
        return listener_name

    @property
    def registered_listeners(self):
        """
        Get all registered listeners
        :return:
        """
        return self._registered_listeners

    def dispose(self):
        self.init_listener.dispose()
        for listener in self.iterating_listener_dict.values():
            listener.dispose()
