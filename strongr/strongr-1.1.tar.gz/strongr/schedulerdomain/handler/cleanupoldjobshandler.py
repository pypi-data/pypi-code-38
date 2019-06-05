from datetime import datetime, timedelta

from sqlalchemy import and_

import strongr.core
from strongr.schedulerdomain.model import Job, JobState


class CleanupOldJobsHandler(object):
    def __call__(self, command):
        """
        MySQL:
        DELETE FROM jobs WHERE state IN ('FINISHED', 'FAILED') AND state_date < DATE_SUB(NOW(), INTERVAL 1 HOUR)
        """

        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        deadline = datetime.utcnow() - timedelta(minutes=120)

        session.delete(Job).filter(and_(Job.state.in_([JobState.FINISHED, JobState.FAILED]), Job.state_date < deadline))
