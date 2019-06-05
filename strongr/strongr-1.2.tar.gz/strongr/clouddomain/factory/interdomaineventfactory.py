from strongr.core.exception import InvalidParameterException

from strongr.clouddomain.event.inter.jobfinished import JobFinished
from strongr.clouddomain.event.inter.vmdestroyed import VmDestroyed
from strongr.clouddomain.event.inter.vmready import VmReady
from strongr.clouddomain.event.inter.vmcreated import VmCreated
from strongr.clouddomain.event.inter.vmnew import VmNew

# try-except for py 2 / 3 compatibility
try:
    basestring
except NameError:
    basestring = str

class InterDomainEventFactory(object):
    def newJobFinishedEvent(self, job_id, ret, retcode):
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('job_id is invalid')
        elif not isinstance(ret, basestring) or len(ret.strip()) == 0:
            raise InvalidParameterException('ret is invalid')
        elif not isinstance(retcode, int):
            raise InvalidParameterException('retcode is invalid')

        return JobFinished(job_id, ret, retcode)

    def newVmDestroyedEvent(self, job_id):
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('job_id not valid')

        return VmDestroyed(job_id)

    def newVmReadyEvent(self, job_id):
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('job_id not valid')

        return VmReady(job_id)

    def newVmCreatedEvent(self, job_id):
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('job_id not valid')

        return VmCreated(job_id)

    def newVmNewEvent(self, job_id, cores, ram):
        if not isinstance(job_id, basestring) or len(job_id.strip()) == 0:
            raise InvalidParameterException('job_id not valid')
        elif not isinstance(cores, int) or cores <= 0:
            raise InvalidParameterException('cores not valid')
        elif not isinstance(ram, int) or cores <= 0:
            raise InvalidParameterException('ram not valid')

        return VmNew(job_id, cores, ram)
