from strongr.core import Core
from strongr.core.domain.clouddomain import CloudDomain
from .wrapper import Command

class ListDeployedVmsCommand(Command):
    """
    List VMs deployed in the cloud.

    deploy:list
    """
    def handle(self):
        cloudService = CloudDomain.cloudService()
        queryFactory = CloudDomain.queryFactory()

        queryBus = cloudService.getQueryBus()
        listDeployedVms = queryFactory.newListDeployedVms()
        print(queryBus.handle(listDeployedVms))
