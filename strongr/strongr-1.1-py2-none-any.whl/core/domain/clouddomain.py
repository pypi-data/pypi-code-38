import dependency_injector.containers as containers
import dependency_injector.providers as providers

from strongr.clouddomain.event.inter.jobfinished import JobFinished
from strongr.clouddomain.event.inter.vmcreated import VmCreated
from strongr.clouddomain.event.inter.vmready import VmReady
from strongr.clouddomain.event.inter.vmdestroyed import VmDestroyed
from strongr.clouddomain.event.inter.vmnew import VmNew

from strongr.clouddomain.factory import CommandFactory, QueryFactory
from strongr.clouddomain.service import CloudServices

import strongr.core

class CloudDomain(containers.DeclarativeContainer):
    """IoC container of service providers."""
    cloudService = providers.Singleton(CloudServices().getCloudServiceByName, strongr.core.Core.config().clouddomain.driver)
    commandFactory = providers.Singleton(CommandFactory)
    queryFactory = providers.Singleton(QueryFactory)

    events = providers.Object({
        'jobfinished': JobFinished,
        'vmnew': VmNew,
        'vmcreated': VmCreated,
        'vmready': VmReady,
        'vmdestroyed': VmDestroyed
    })
