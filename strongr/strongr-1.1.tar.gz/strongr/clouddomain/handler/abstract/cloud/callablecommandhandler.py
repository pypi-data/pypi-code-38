from abc import ABCMeta, abstractmethod

import strongr.core
class CallableCommandHandler:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __call__(self, command):
        pass

    def executeAndPublishDomainEvent(self, event, callable, **kwargs):
        callable(*kwargs)
        self.publishDomainEvent(event)

    def publishDomainEvent(self, event):
        core = strongr.core.getCore()
        core.domainEventsPublisher().publish(event)
