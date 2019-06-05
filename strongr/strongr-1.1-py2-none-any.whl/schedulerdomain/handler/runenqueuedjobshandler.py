import strongr.core
import strongr.core.domain.schedulerdomain
import strongr.core.gateways

class RunEnqueuedJobsHandler:
    def __call__(self, command):
        # this command should be simplified at some point
        # finding jobs and a vm to run the job on could be
        # done in one sql query for example.

        SchedulerDomain = strongr.core.domain.schedulerdomain.SchedulerDomain

        schedulerService = SchedulerDomain.schedulerService()
        commandBus = schedulerService.getCommandBus()

        queryBus = schedulerService.getQueryBus()
        queryFactory = SchedulerDomain.queryFactory()

        commandFactory = SchedulerDomain.commandFactory()

        jobs = queryBus.handle(queryFactory.newRequestScheduledJobs()) # this query only gives us JobState enqueued and assigned jobs

        for job in jobs:
            # task is not running, let's try to execute it on an available node
            vm_id = queryBus.handle(queryFactory.newFindNodeWithAvailableResources(job.cores, job.ram))
            if vm_id == None:
                continue

            commandBus.handle(commandFactory.newStartJobOnVm(vm_id, job.job_id))
