import strongr.core

from sqlalchemy import func

from strongr.schedulerdomain.model import Job, JobState


class RequestResourcesRequiredHandler(object):
    def __call__(self, query):
        db = strongr.core.gateways.Gateways.sqlalchemy_session()

        results = db.query(func.count(Job.cores).label('cores'), func.count(Job.ram).label('ram')).filter(Job.state == JobState.ENQUEUED).all()

        if results:
            return {'cores': results[0][0], 'ram': results[0][1]}
        return None
