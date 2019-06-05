from strongr.schedulerdomain.model.scalingdrivers.abstract import AbstractScaleOut, AbstractScaleIn, \
    AbstractVmTemplateRetriever

import uuid

import strongr.core
import strongr.core.gateways
import logging
import strongr.core.domain.schedulerdomain

from sqlalchemy import func, and_, or_

from strongr.schedulerdomain.model import JobState, Job, Vm, VmState

from datetime import datetime, timedelta

# This scaler is specifically written for the Surf-SARA HPCCloud

class SurfHpcScaler(AbstractScaleIn, AbstractScaleOut, AbstractVmTemplateRetriever):
    def __init__(self, config, *args, **kwargs):
        super(SurfHpcScaler, self).__init__(*args, **kwargs)
        self._config = config

    def get_vm_max_age(self, vm_name):
        deadline = datetime.utcnow() + timedelta(hours=6)
        return deadline

    def get_templates(self):
        return self._config['templates']

    def scalein(self, command):
        if strongr.core.gateways.Gateways.lock('scaleout-lock').exists():
            return # only every run one of these commands at once

        # double check lock
        # we should move this locking mechanism a little bit more down the chain so that it isn't the specific scaling
        # algorithms responsibility
        with strongr.core.gateways.Gateways.lock('scaleout-lock'):  # only ever run one of these commands at once
            logger = logging.getLogger('schedulerdomain.' + self.__class__.__name__)

            session = strongr.core.gateways.Gateways.sqlalchemy_session()

            # subquery to see whats already running on vm
            subquery1 = session.query(Job.vm_id, func.count(Job.job_id).label('jobs'), func.sum(Job.cores).label('cores'), func.sum(Job.ram).label('ram')).filter(
                Job.state.in_([JobState.RUNNING])).group_by(Job.vm_id).subquery('j')

            subquery2 = session.query(Job.vm_id, func.max(Job.state_date).label('last_job_date')).filter(Job.state.in_([JobState.FAILED, JobState.FINISHED, JobState.RUNNING])).group_by(Job.vm_id).subquery('i')

            job_deadline = datetime.utcnow() + timedelta(minutes=-10)

            results = session.query(Vm.vm_id.label('vm_id'), subquery1.c.jobs.label('job_count'), subquery2.c.last_job_date) \
                .outerjoin(subquery1, subquery1.c.vm_id == Vm.vm_id) \
                .outerjoin(subquery2, subquery2.c.vm_id == Vm.vm_id) \
                .filter(
                and_(
                    and_(  # only vm's with no jobs
                        subquery1.c.cores == None,
                        subquery1.c.ram == None,
                    ),
                    or_(
                        subquery2.c.last_job_date < job_deadline, # if no job running for 10 minutes kill the vm
                        and_(subquery2.c.last_job_date == None, Vm.state_date < job_deadline) # if no job scheduled to vm for 10 minutes kill the vm
                    ),
                    Vm.state.in_([VmState.READY])  # vm should be in state ready
                )
            ).all()

            if not results:
                return # no VM's to scalein

            vms_to_update = []
            for vm in results:
                vms_to_update.append(vm[0])

            if len(vms_to_update) > 0:
                    session.query(Vm).filter(Vm.vm_id.in_(vms_to_update)).update({Vm.state: VmState.MARKED_FOR_DEATH}, synchronize_session='fetch')

    def scaleout(self, command):
        cores = command.cores
        ram = command.ram

        if strongr.core.gateways.Gateways.lock('scaleout-lock').exists():
            return # only every run one of these commands at once

        with strongr.core.gateways.Gateways.lock('scaleout-lock'):  # only ever run one of these commands at once
            config = self._config
            logger = logging.getLogger('schedulerdomain.' + self.__class__.__name__)

            query_factory = strongr.core.domain.schedulerdomain.SchedulerDomain.queryFactory()
            query_bus = strongr.core.domain.schedulerdomain.SchedulerDomain.schedulerService().getQueryBus()

            templates = dict(config['templates']) # make a copy because we want to manipulate the list

            active_vms = query_bus.handle(query_factory.newRequestVms([VmState.NEW, VmState.PROVISION, VmState.READY]))

            provision_counter = 0
            for vm in active_vms:
                if vm.state in [VmState.NEW, VmState.PROVISION]:
                    cores -= vm.cores
                    ram -= vm.ram
                    provision_counter += 1

            if provision_counter >= 2:
                # don't provision more than 2 VM's at the same time
                return

            for template in templates:
                templates[template]['distance'] = templates[template]['ram'] / templates[template]['cores']

            ram_per_core_needed = ram / cores

            # find best fit based on templates

            # first we calculate the distance based on optimal mem / core distribution
            distances = {}
            for template in templates:
                distance = abs(templates[template]['distance'] - ram_per_core_needed)
                if distance not in distances:
                    distances[distance] = []
                distances[distance].append(template)

            min_distance_templates = distances[min(distances)] # get templates with least distance

            # now find the templates with resources that best fit what we need
            # we simply select the best fitting template with the most resources
            template = min(min_distance_templates, key=lambda key: (cores - templates[key]['cores']) + (ram - templates[key]['ram']))

            # scaleout by one instance
            cloudService = strongr.core.domain.clouddomain.CloudDomain.cloudService()
            cloudCommandFactory = strongr.core.domain.clouddomain.CloudDomain.commandFactory()
            profile = config['default_profile'] if 'profile' not in templates[template] else templates[template]['profile']
            deployVmsCommand = cloudCommandFactory.newDeployVms(names=[template + '-' + str(uuid.uuid4())], profile=profile, cores=templates[template]['cores'], ram=templates[template]['ram'])

            cloudCommandBus = cloudService.getCommandBus()

            logger.info('Deploying VM {0} cores={1} ram={2}GiB'.format(deployVmsCommand.names[0], templates[template]['cores'], templates[template]['ram']))

            cloudCommandBus.handle(deployVmsCommand)
