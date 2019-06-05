import strongr.core.domain.schedulerdomain

class CheckScalingHandler(object):
    def __call__(self, command):
        query_bus = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getQueryBus()
        command_bus = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getCommandBus()

        query_factory = strongr.core.domain.schedulerdomain.SchedulerDomain.queryFactory()
        command_factory = strongr.core.domain.schedulerdomain.SchedulerDomain.commandFactory()

        resources_required = query_bus.handle(query_factory.newRequestResourcesRequired())

        if resources_required is None or (resources_required['cores'] == 0 and resources_required['ram'] == 0):
            # scalein
            command_bus.handle(command_factory.newScaleIn())
        elif resources_required['cores'] > 0:
            # scaleout
            command_bus.handle(command_factory.newScaleOut(resources_required['cores'], resources_required['ram']))
