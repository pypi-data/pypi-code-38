import unittest

from strongr.schedulerdomain.model import Job, JobState
import strongr.core.gateways
import strongr.core.domain.schedulerdomain

class TestJobFinished(unittest.TestCase):
    def test_job_finished(self):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        session.query(Job).filter(Job.job_id == 'unittestjob').delete()

        job = Job()
        job.job_id = 'unittestjob'
        job.cmd = 'ls -l'
        job.cores = 1
        job.ram = 1
        job.state = JobState.ENQUEUED

        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        session.add(job)
        session.commit()

        factory = strongr.core.domain.schedulerdomain.SchedulerDomain.commandFactory()
        job_finished = factory.newJobFinished(job.job_id, 'Testing jobfinished command', 0)
        strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getCommandBus().handle(job_finished)

        self.assertEqual(job.state, JobState.FINISHED)

        session.query(Job).filter(Job.job_id == 'unittestjob').delete()
