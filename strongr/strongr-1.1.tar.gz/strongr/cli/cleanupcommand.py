from .wrapper import Command

import strongr.core.domain.schedulerdomain

class CleanupCommand(Command):
    """
    Run cleanup jobs

    deploy:cleanup
    """
    def handle(self):
        command_factory = strongr.core.domain.schedulerdomain.SchedulerDomain.commandFactory()
        command_bus = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getCommandBus()

        command_bus.handle(command_factory.newCleanupNodes())
