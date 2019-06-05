from sqlalchemy import func

import strongr.core
from strongr.core.gateways import Gateways
from strongr.schedulerdomain.model import Vm, VmState, Job, JobState


class LogStatsHandler(object):
    def __call__(self, command):
        if strongr.core.Core.config().stats.driver.lower() == 'null':
            return # skip collecting stats, nulldriver is selected

        session = Gateways.sqlalchemy_session()
        stats = Gateways.stats()

        # number of VM's, cores, ram
        active_vms = session.query(
            func.count(Vm.vm_id),
            func.sum(Vm.cores),
            func.sum(Vm.ram)
        ).filter(Vm.state.in_([VmState.READY, VmState.MARKED_FOR_DEATH])).all()

        if len(active_vms) > 0:
            active_vms = active_vms[0] # only 1 row is returned
            namespace = 'stats.vms.active.'
            stats.gauge(namespace + 'count', active_vms[0] if active_vms[0] is not None else 0)
            stats.gauge(namespace + 'cores', active_vms[1] if active_vms[1] is not None else 0)
            stats.gauge(namespace + 'ram', active_vms[2] if active_vms[2] is not None else 0)

        # number of active jobs, cores used, ram used
        active_jobs = session.query(
            func.count(Job.job_id),
            func.sum(Job.cores),
            func.sum(Job.ram)
        ).filter(Job.state == JobState.RUNNING).all()

        if len(active_jobs) > 0:
            active_jobs = active_jobs[0] # only 1 row is returned
            namespace = 'stats.jobs.running.'
            stats.gauge(namespace + 'count', active_jobs[0] if active_jobs[0] is not None else 0)
            stats.gauge(namespace + 'cores', active_jobs[1] if active_jobs[1] is not None else 0)
            stats.gauge(namespace + 'ram', active_jobs[2] if active_jobs[2] is not None else 0)

        # number of enqueued jobs, cores needed, ram needed
        enqueued_jobs = session.query(
            func.count(Job.job_id),
            func.sum(Job.cores),
            func.sum(Job.ram)
        ).filter(Job.state == JobState.ENQUEUED).all()

        if len(enqueued_jobs) > 0:
            enqueued_jobs = enqueued_jobs[0]  # only 1 row is returned
            namespace = 'stats.jobs.enqueued.'
            stats.gauge(namespace + 'count', enqueued_jobs[0] if enqueued_jobs[0] is not None else 0)
            stats.gauge(namespace + 'cores', enqueued_jobs[1] if enqueued_jobs[1] is not None else 0)
            stats.gauge(namespace + 'ram', enqueued_jobs[2] if enqueued_jobs[2] is not None else 0)

        # number of failed jobs, cores needed, ram needed
        failed_jobs = session.query(
            func.count(Job.job_id)
        ).filter(Job.state == JobState.FAILED).all()

        if len(failed_jobs) > 0:
            failed_jobs = failed_jobs[0]  # only 1 row is returned
            namespace = 'stats.jobs.failed.'
            stats.gauge(namespace + 'count', failed_jobs[0] if failed_jobs[0] is not None else 0)
