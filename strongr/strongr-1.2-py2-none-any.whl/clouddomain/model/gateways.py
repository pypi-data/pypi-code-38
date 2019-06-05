import dependency_injector.containers as containers
import dependency_injector.providers as providers

import strongr.core.eventspublisher
import strongr.clouddomain.model.salt.salteventtranslator

import strongr.clouddomain.factory.intradomaineventfactory as intradomaineventfactory
import strongr.clouddomain.factory.interdomaineventfactory as interdomainfactory

import strongr.clouddomain.event.intra.saltjobfinished as saltjobfinished

import strongr.core.domain.clouddomain


class Gateways(containers.DeclarativeContainer):
    inter_domain_event_factory = providers.Singleton(interdomainfactory.InterDomainEventFactory)
    intra_domain_event_factory = providers.Singleton(intradomaineventfactory.IntraDomainEventFactory)

    intra_domain_events_publisher = providers.Singleton(strongr.core.eventspublisher.EventsPublisher, 'CloudDomain')
    domain_event_bindings = providers.Object({
        saltjobfinished.SaltJobFinished: { # command / query generators based on event
            #'command': [
            #    #(lambda event: strongr.core.domain.clouddomain.CloudDomain.commandFactory().newJobFinishedCommand(event.jid, event.ret, event.retcode))
            #],
            #'escalate-to-inter': [ # escalate event to inter-domain event
            #    #(lambda event: Gateways.inter_domain_event_factory().newJobFinishedEvent(event.jid, event.ret, event.retcode))
            #]
        }
    })
    salt_event_translator = providers.Singleton(strongr.clouddomain.model.salt.salteventtranslator.SaltEventTranslator, name="SaltEventTranslator")
