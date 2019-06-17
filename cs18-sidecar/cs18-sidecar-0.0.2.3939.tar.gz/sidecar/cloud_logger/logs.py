from abc import abstractmethod, ABCMeta
from datetime import datetime
from typing import List, Tuple


class ILogEntry(metaclass=ABCMeta):
    def __init__(self, log_events: List[Tuple[datetime, str]], log_type: str):
        self.log_type = log_type
        self.log_events = log_events

    @abstractmethod
    def get_log_filepath(self, basepath: str) -> str:
        raise NotImplemented()

    @abstractmethod
    def get_as_string(self) -> str:
        raise NotImplemented()


class AppLogEntry(ILogEntry):
    def __init__(self, app: str, instance: str, topic: str, log_events: List[Tuple[datetime, str]], log_type: str):
        super().__init__(log_events, log_type)
        self.app = app
        self.instance = instance
        self.topic = topic

    def get_as_string(self) -> str:
        log_events_str = "\n".join(str(time) + " " + message for time, message in self.log_events)
        return "app: " + self.app + "\ninstance: " + self.instance + "\ntopic: " + self.topic + "\n" + log_events_str

    def get_log_filepath(self, basepath: str) -> str:
        instance_id = self.instance.replace("docker://", "")
        return f"{basepath}/{instance_id}.{self.app}-{self.log_type}.log"


class ServiceLogEntryLogType:
    LOG = "LOG"
    ERROR = "ERROR"


class ServiceLogEntry(ILogEntry):
    def __init__(self,
                 name: str,
                 log_events: List[Tuple[datetime, str]],
                 log_type: str):
        super().__init__(log_events, log_type)
        self.service = name

    def get_log_filepath(self, basepath: str) -> str:
        return f"{basepath}/{self.service}.service-{self.log_type}.log"

    def get_as_string(self) -> str:
        events = "\n".join(str(time) + " " + message for time, message in self.log_events)
        return "service: {SERVICE}\n" \
               "events:\n" \
               "{EVENTS}".format(SERVICE=self.service, EVENTS=events)

