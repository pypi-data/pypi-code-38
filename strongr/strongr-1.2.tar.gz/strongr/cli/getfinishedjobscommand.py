from strongr.core.domain.schedulerdomain import SchedulerDomain
from .wrapper import Command

import json

class GetFinishedJobsCommand(Command):
    """
    Returns all finished jobs.

    jobs:finished
    """
    def handle(self):
        schedulerService = SchedulerDomain.schedulerService()
        queryFactory = SchedulerDomain.queryFactory()

        query = queryFactory.newRequestFinishedJobs()
        result = schedulerService.getQueryBus().handle(query)
        print(json.dumps(result))
