import strongr.core

import strongr.core.domain.schedulerdomain
import strongr.core.domain.clouddomain
import strongr.core.gateways

from sqlalchemy import and_
from datetime import datetime, timedelta

from strongr.schedulerdomain.model import Job, JobState


class CheckJobsRunningHandler:
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        deadline = datetime.utcnow() - timedelta(minutes=15)

        for job in session.query(Job).filter(and_(Job.state == JobState.RUNNING, Job.state_date < deadline)).all():
            cloudQueryBus = strongr.core.domain.clouddomain.CloudDomain.cloudService().getQueryBus()
            cloudQueryFactory = strongr.core.domain.clouddomain.CloudDomain.queryFactory()

            status = cloudQueryBus.handle(cloudQueryFactory.newRequestJidStatus(job.job_id))

            if status is None or not status:
                # job not finished yet
                continue

            session.query(Job).filter(Job.job_id == job.job_id).update({Job.stdout: status[list(status.keys())[0]], Job.return_code: 0, Job.state: JobState.FINISHED}, synchronize_session='evaluate')
