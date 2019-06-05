import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.schedulerdomain.service import SchedulerService
from strongr.schedulerdomain.factory import CommandFactory, QueryFactory

import strongr.core.domain.clouddomain

class SchedulerDomain(containers.DeclarativeContainer):
    """IoC container of service providers."""
    inter_domain_event_bindings = providers.Object({
        strongr.core.domain.clouddomain.CloudDomain.events()['jobfinished']: {  # command / query generators based on event
            'command': [
                (lambda event: SchedulerDomain.commandFactory().newJobFinished(event.job_id, event.ret, event.retcode))#,
                #(lambda event: SchedulerDomain.commandFactory().newRunEnqueuedJobs())
            ]
        },
        strongr.core.domain.clouddomain.CloudDomain.events()['vmnew']: {
            'command': [
                (lambda event: SchedulerDomain.commandFactory().newVmNew(event.vm_id, event.cores, event.ram))
            ]
        },
        strongr.core.domain.clouddomain.CloudDomain.events()['vmcreated']: {
            'command': [
                (lambda event: SchedulerDomain.commandFactory().newVmCreated(event.vm_id))
            ]
        },
        strongr.core.domain.clouddomain.CloudDomain.events()['vmready']: {
            'command': [
                (lambda event: SchedulerDomain.commandFactory().newVmReady(event.vm_id))
            ]
        },
        strongr.core.domain.clouddomain.CloudDomain.events()['vmdestroyed']: {
            'command': [
                (lambda event: SchedulerDomain.commandFactory().newVmDestroyed(event.vm_id))
            ]
        }
    })

    schedulerService = providers.Singleton(SchedulerService, inter_domain_event_bindings())
    commandFactory = providers.Singleton(CommandFactory)
    queryFactory = providers.Singleton(QueryFactory)
