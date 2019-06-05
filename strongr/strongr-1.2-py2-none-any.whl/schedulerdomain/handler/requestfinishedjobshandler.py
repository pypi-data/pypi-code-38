from sqlalchemy import and_

import strongr.core.gateways
from strongr.schedulerdomain.model import Job, JobState

class RequestFinishedJobsHandler(object):
    def __call__(self, query, *args, **kwargs):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        if query.jobs is not None:
            result = session.query(Job).filter(and_(Job.state.in_([JobState.FAILED, JobState.FINISHED]), Job.job_id.in_(query.jobs))).order_by(
            Job.job_id).all()
        else:
            result = session.query(Job).filter(Job.state.in_([JobState.FAILED, JobState.FINISHED])).order_by(
                Job.job_id).all()

        job_ids = []
        for job in result:
            job_ids.append(job.job_id)
        return job_ids
