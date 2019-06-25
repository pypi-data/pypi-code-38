from abc import abstractmethod

from api.handler import HandlerEnum


class IHandler:

    @abstractmethod
    def handler_enum(self)->HandlerEnum:
        pass