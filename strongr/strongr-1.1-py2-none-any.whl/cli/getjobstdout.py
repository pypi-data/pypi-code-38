from strongr.core.domain.schedulerdomain import SchedulerDomain
from .wrapper import Command

import strongr.core.domain.schedulerdomain
import json

class GetJobStdOut(Command):
    """
    Returns a jobs stdout

    job:stdout
        {jid : The job id to be checked}
    """
    def handle(self):
        query_factory = strongr.core.domain.schedulerdomain.SchedulerDomain.queryFactory()
        query_bus = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getQueryBus()

        command = query_factory.newRequestTaskInfo(self.argument('jid'))

        result = query_bus.handle(command)

        if result is None:
            print(json.dumps({}))
            return

        print(json.dumps({'job_id': result.job_id, 'stdout': result.stdout}))
