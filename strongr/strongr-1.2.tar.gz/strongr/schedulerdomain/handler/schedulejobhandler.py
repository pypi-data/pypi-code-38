import strongr.core.gateways
from strongr.schedulerdomain.model import Job, JobState


class ScheduleJobHandler:
    def __call__(self, command):
        job = Job()
        job.image = command.image
        job.script = "\n".join(command.script)
        job.job_id = command.job_id
        job.scratch = command.scratch
        job.cores = command.cores
        job.ram = command.memory
        job.state = JobState.ENQUEUED
        job.vm = None

        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        session.add(job)
        session.commit()
