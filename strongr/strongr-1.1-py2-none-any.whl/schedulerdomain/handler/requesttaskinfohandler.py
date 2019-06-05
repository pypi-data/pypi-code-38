from strongr.schedulerdomain.model import Job
import strongr.core.gateways

class RequestTaskInfoHandler:
    def __call__(self, query):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        result = session.query(Job).filter(Job.job_id.in_(query.jobs)).all()
        return result
