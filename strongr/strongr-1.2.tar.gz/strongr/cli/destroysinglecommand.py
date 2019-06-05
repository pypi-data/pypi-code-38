from strongr.core import Core
from strongr.core.domain.clouddomain import CloudDomain
from .wrapper import Command

class DestroySingleCommand(Command):
    """
    Destroys a VM in the cloud.

    destroy:single
        {machine : The name of the VM to be destroyed}
    """
    def handle(self):
        cloudService = CloudDomain.cloudService()
        commandFactory = CloudDomain.commandFactory()

        machine = self.argument('machine')
        destroyVmsCommand = commandFactory.newDestroyVms(names=[machine])

        commandBus = cloudService.getCommandBus()

        self.info('Destroying VM {0}'.format(machine))

        commandBus.handle(destroyVmsCommand)
