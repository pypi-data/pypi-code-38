import strongr.core.gateways

from strongr.schedulerdomain.model import Job, JobState

class JobFinishedHandler(object):
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        jobstate = (JobState.FINISHED if command.retcode == 0 else JobState.FAILED)
        session.query(Job).filter(Job.job_id == command.job_id).update(
            {
                Job.state: jobstate,
                Job.stdout: command.ret,
                Job.return_code: command.retcode
            },
            synchronize_session='fetch'
        )
