import json

from strongr.core.domain.schedulerdomain import SchedulerDomain
from .wrapper import Command

class RequestScheduledTasks(Command):
    """
    Shows the task queue.

    job:list
    """
    def handle(self):
        schedulerService = SchedulerDomain.schedulerService()
        queryFactory = SchedulerDomain.schedulerQueryFactory()

        query = queryFactory.newRequestScheduledJobs()
        result = schedulerService.getQueryBus().handle(query)
        print(json.dumps(result))

