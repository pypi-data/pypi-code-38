from typing import Union, Callable, Any
from treelab.event_handling.listener import Listener, EventPayload, FunctionListener
from treelab.consts import Source
from abc import ABC, abstractmethod


class Listenable(ABC):
    def __init__(self, workspace):
        self._workspace = workspace

    @property
    def workspace(self):
        return self._workspace

    @abstractmethod
    def listen_to(self, listener: Union[Callable[[EventPayload], Any], Listener], name: str = None,
                  thread_num: int = 0, user_only: bool = True, local_listen=False):
        """
        Register a listener to the object, it will not subscribe until self.workspace.subscribe is called
        :param listener:
        :param name:
        :param thread_num:
        :param user_only:
        :param local_listen:
        :return:
        """
        pass

    def get_row(self, event: EventPayload):
        return self.get_table(event).row(event.rowId)

    def get_table(self, event: EventPayload):
        return self.get_core(event).table(event.tableId)

    def get_core(self, event: EventPayload):
        return self.workspace.core(event.coreId)


class BasicListenable(Listenable, ABC):
    def __init__(self, workspace):
        super().__init__(workspace)

    @abstractmethod
    def should_be_listened(self, event: EventPayload, listener: Listener):
        pass

    def listen_to(self, listener: Union[Callable[[EventPayload], Any], Listener], name: str = None,
                  thread_num: int = 0, user_only: bool = True, local_listen=False):
        """
        Register a listener to the object, it will not subscribe until self.workspace.subscribe is called
        :param listener:
        :param name:
        :param thread_num:
        :param user_only:
        :param local_listen:This is used to listen for the end of the API request GRPC, please do not fill in True
        :return:
        """
        if not isinstance(listener, Listener):
            listener = FunctionListener(listener, name=name)

        listener.listenable_list.append(self)

        def listener_func(event: EventPayload):
            if local_listen and not user_only and Source(event._metadata.source) is Source.EXTERNAL_API:
                if self.should_be_listened(event=event, listener=listener):
                    listener.run(event)
            elif (not user_only) or (user_only and Source(event._metadata.source) in [Source.USER, Source.SAGA]):
                if self.should_be_listened(event=event, listener=listener):
                    listener.run(event)

        function_listener = FunctionListener(listener_func, name=name)
        self.workspace.register(function_listener, thread_num=thread_num)
