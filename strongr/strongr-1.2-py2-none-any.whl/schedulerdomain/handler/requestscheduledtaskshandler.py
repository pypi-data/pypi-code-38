import strongr.core.gateways
from strongr.schedulerdomain.model import Job, JobState

class RequestScheduledTasksHandler:
    def __call__(self, query):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        result = session.query(Job).filter(Job.state.in_([JobState.ASSIGNED, JobState.ENQUEUED])).order_by(Job.job_id).limit(query.limit).all()
        return result
