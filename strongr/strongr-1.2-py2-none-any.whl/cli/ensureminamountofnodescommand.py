import strongr.core.domain.schedulerdomain
from .wrapper import Command

class EnsureMinAmountOfNodesCommand(Command):
    """
    Ensure the minimum amount of nodes is spawned.

    deploy:environment
    """
    def handle(self):
        schedulerService = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService()
        commandFactory = strongr.core.domain.schedulerdomain.SchedulerDomain.commandFactory()

        command = commandFactory.newEnsureMinAmountOfNodes()
        schedulerService.getCommandBus().handle(command)
