from abc import ABCMeta, abstractmethod

from cmndr import CommandBus
from cmndr.handlers import CommandHandler
from cmndr.handlers.inflectors import CallableInflector
from cmndr.handlers.locators import LazyLoadingInMemoryLocator
from cmndr.handlers.nameextractors import ClassNameExtractor

from strongr.clouddomain.handler.abstract.cloud import AbstractDestroyVmsHandler, AbstractDeployVmsHandler, \
                                                        AbstractListDeployedVmsHandler, AbstractRunJobHandler,\
                                                        AbstractRequestJidStatusHandler, AbstractJobFinishedHandler

from strongr.clouddomain.command import DestroyVms, DeployVms, RunJob, JobFinished
from strongr.clouddomain.query import ListDeployedVms, RequestJidStatus

import strongr.clouddomain.model.gateways as gateways
import strongr.core as core

class AbstractCloudService():
    __metaclass__ = ABCMeta
    _commands = {}
    _queries = {}


    _mappings = {
        AbstractListDeployedVmsHandler: ListDeployedVms.__name__,
        AbstractRunJobHandler: RunJob.__name__,
        AbstractDeployVmsHandler: DeployVms.__name__,
        AbstractRequestJidStatusHandler: RequestJidStatus.__name__,
        AbstractDestroyVmsHandler: DestroyVms.__name__,
        AbstractJobFinishedHandler: JobFinished.__name__
    }

    def __init__(self):
        # map commands and handlers
        for handler in self.get_command_handlers():
            command = self._getCommandForHandler(handler)
            self._commands[handler] = command
        for handler in self.get_query_handlers():
            command = self._getCommandForHandler(handler)
            self._queries[handler] = command

        # map events to commands / queries
        event_bindings = gateways.Gateways.domain_event_bindings()
        for event in event_bindings:
            if 'command' in event_bindings[event]:
                for command_generator in event_bindings[event]['command']:
                    gateways.Gateways.intra_domain_events_publisher().subscribe(event, (lambda event, command_generator=command_generator: self.getCommandBus().handle(command_generator(event))))
            if 'query' in event_bindings[event]:
                for query_generator in event_bindings[event]['query']:
                    gateways.Gateways.intra_domain_events_publisher().subscribe(event, (lambda event, query_generator=query_generator: self.getQueryBus().handle(query_generator(event))))
            if 'escalate-to-inter' in event_bindings[event]: # escalate intra-event to inter-event
                for inter_domain_event_generator in event_bindings[event]['escalate-to-inter']:
                    gateways.Gateways.intra_domain_events_publisher().subscribe(event, (lambda event, inter_domain_event_generator=inter_domain_event_generator: core.Core.inter_domain_events_publisher().publish(inter_domain_event_generator(event))))



    @abstractmethod
    def get_command_handlers(self):
        return

    @abstractmethod
    def get_query_handlers(self):
        pass

    def _getCommandForHandler(self, handler):
        for mappedHandler in self._mappings:
            if issubclass(handler, mappedHandler):
                command = self._mappings[mappedHandler]
                # remove from self._mappings so that a handler with multiple inheritance can work
                del self._mappings[mappedHandler]
                return command
        return None

    def _makeBus(self, handlers, middlewares=None):
        extractor = ClassNameExtractor()
        locator = LazyLoadingInMemoryLocator(handlers)
        inflector = CallableInflector()
        handler = CommandHandler(extractor, locator, inflector)
        if middlewares != None:
            return CommandBus(middlewares + [handler])
        return CommandBus([handler])

    def getCommandBus(self, middlewares=None):
        if not hasattr(self, '_commandbus'):
            self._commandbus = self._makeBus(self._commands, middlewares)
        return self._commandbus

    def getQueryBus(self, middlewares=None):
        if not hasattr(self, '_querybus'):
            self._querybus = self._makeBus(self._queries, middlewares)
        return self._querybus
