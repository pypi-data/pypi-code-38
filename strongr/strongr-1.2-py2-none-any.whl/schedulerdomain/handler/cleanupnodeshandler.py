import strongr.core.domain.clouddomain
from sqlalchemy import and_, or_, func
from strongr.schedulerdomain.model import Vm, VmState, Job, JobState
from datetime import datetime, timedelta

import strongr.core
from strongr.schedulerdomain.model.scalingdrivers import ScalingDriver


class CleanupNodesHandler(object):
    def __call__(self, command):
        # VM's killed in the cloud are not yet synchronized to local db

        cloud_command_factory = strongr.core.domain.clouddomain.CloudDomain.commandFactory()
        cloud_command_bus = strongr.core.domain.clouddomain.CloudDomain.cloudService().getCommandBus()
        cloud_query_factory = strongr.core.domain.clouddomain.CloudDomain.queryFactory()
        cloud_query_bus = strongr.core.domain.clouddomain.CloudDomain.cloudService().getQueryBus()

        vm_templates = ScalingDriver.scaling_driver().get_templates()

        deadline = datetime.utcnow() + timedelta(minutes=-30) # give cloud domain time to provision a machine, if it isn't online by then it will probably never be
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        unprovisioned_vms_in_db = session.query(Vm).filter(and_(Vm.state.in_([VmState.NEW, VmState.PROVISION]), deadline > Vm.state_date)).all()
        vms_in_cloud = cloud_query_bus.handle(cloud_query_factory.newListDeployedVms())

        parallel_remove_list = []
        for vm in unprovisioned_vms_in_db:
            if vm.vm_id in vms_in_cloud['up'] or vm in vms_in_cloud['down']:
                vm.state = VmState.MARKED_FOR_DEATH
            else: # vm was never up or manually destroyed
                vm.state = VmState.FAILURE

        session.commit() # execute update queries

        vms_in_db = [vm[0] for vm in session.query(Vm.vm_id).filter(
            and_(Vm.state.in_([VmState.NEW, VmState.PROVISION, VmState.READY, VmState.MARKED_FOR_DEATH]))).all()]

        # cleanup unsynced / unregistered VM's
        for template in vm_templates:
            for vm in vms_in_cloud['up']:
                if vm not in vms_in_db and vm.startswith(template + '-'):
                    parallel_remove_list.append(vm)

            for vm in vms_in_cloud['down']:
                if vm not in vms_in_db and vm.startswith(template + '-'):
                    parallel_remove_list.append(vm)

        # check for VM's marked for death without jobs
        deadline = datetime.utcnow() + timedelta(seconds=-10) # vm's need to be marked for death for at least 10 secs before we clean them up else we run into race conditions
        subquery = session.query(Job.vm_id,
                                 func.count(Job.job_id).label('jobs'))\
                                .filter(
                                    Job.state.in_([JobState.ASSIGNED, JobState.RUNNING])
                                ).group_by(Job.vm_id).subquery('j')
        marked_for_death_vms = session.query(Vm)\
            .outerjoin(subquery, subquery.c.vm_id == Vm.vm_id)\
            .filter(and_(Vm.state == VmState.MARKED_FOR_DEATH, or_(subquery.c.jobs == None, subquery.c.jobs == 0),  deadline > Vm.state_date))\
            .all()

        for vm in marked_for_death_vms:
            parallel_remove_list.append(vm.vm_id)

        # check for expired VM's
        timenow = datetime.utcnow()
        expired_vms = session.query(Vm).filter(and_(timenow > Vm.deadline, Vm.state.in_([VmState.NEW, VmState.PROVISION, VmState.READY]))).all()
        for vm in expired_vms:
            vm.state = VmState.MARKED_FOR_DEATH
        session.commit()

        # send vm destroy command to clouddomain
        if len(parallel_remove_list) > 0:
            command = cloud_command_factory.newDestroyVms(parallel_remove_list)
            cloud_command_bus.handle(command)
