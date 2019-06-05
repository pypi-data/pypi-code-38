import strongr
import strongr.core.domain.clouddomain
from strongr.core.gateways import Gateways
from strongr.schedulerdomain.model import Job, JobState


class StartJobOnVmHandler:
    def __call__(self, command):
        db = strongr.core.gateways.Gateways.sqlalchemy_session()
        db.query(Job).filter(Job.job_id == command.job_id).update({Job.vm_id: command.vm_id, Job.state: JobState.RUNNING}, synchronize_session='fetch')
        db.commit()

        job = db.query(Job).filter(Job.job_id == command.job_id).all()[0]

        cloudCommandBus = strongr.core.domain.clouddomain.CloudDomain.cloudService().getCommandBus()
        cloudCommandFactory = strongr.core.domain.clouddomain.CloudDomain.commandFactory()

        cloudCommandBus.handle(cloudCommandFactory.newRunJob(host=command.vm_id, image=job.image, script=job.script.splitlines(), job_id=job.job_id, scratch=job.scratch, cores=job.cores, memory=job.ram))
