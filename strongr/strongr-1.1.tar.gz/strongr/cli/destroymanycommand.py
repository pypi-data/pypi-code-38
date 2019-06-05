from strongr.core import Core
from strongr.core.domain.clouddomain import CloudDomain
from .wrapper import Command

class DestroyManyCommand(Command):
    """
    Destroys a list of VMs in the cloud.

    destroy:many
        {machines* : The names of the VMs to be destroyed}
    """
    def handle(self):
        cloudService = CloudDomain.cloudService()
        commandFactory = CloudDomain.commandFactory()

        machines = self.argument('machines')

        destroyVmsCommand = commandFactory.newDestroyVms(names=machines)

        commandBus = cloudService.getCommandBus()

        self.info('Destroying VMs {0}'.format(machines))

        commandBus.handle(destroyVmsCommand)
