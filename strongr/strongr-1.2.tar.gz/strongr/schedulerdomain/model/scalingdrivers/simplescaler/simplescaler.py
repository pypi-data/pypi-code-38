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

# The most basic scaler.

class SimpleScaler(AbstractScaleIn, AbstractScaleOut, AbstractVmTemplateRetriever):
    def __init__(self, config, *args, **kwargs):
        super(SimpleScaler, self).__init__(*args, **kwargs)
        self._config = config

    def get_vm_max_age(self, vm_name):
        template = vm_name.vm_id.split('-')[0]
        if len(template) > 0:
            templates = self.get_templates()
            for t in templates:
                if t == template:
                    deadline = datetime.utcnow() + timedelta(seconds=(templates[t]['maxage'] if hasattr(templates[t], 'maxage') else 900))
        else:
            deadline = datetime.utcnow() + timedelta(minutes=15)

        return deadline

    def get_templates(self):
        return self._config.schedulerdomain.simplescaler.templates.as_dict()

    def scalein(self, command):
        if strongr.core.gateways.Gateways.lock('scaleout-lock').exists():
            return # only every run one of these commands at once

        with strongr.core.gateways.Gateways.lock('scaleout-lock'):  # only ever run one of these commands at once
            logger = logging.getLogger('schedulerdomain.' + self.__class__.__name__)

            session = strongr.core.gateways.Gateways.sqlalchemy_session()

            # subquery to see whats already running on vm
            subquery1 = session.query(Job.vm_id, func.count(Job.job_id).label('jobs'), func.sum(Job.cores).label('cores'), func.sum(Job.ram).label('ram')).filter(
                Job.state.in_([JobState.RUNNING])).group_by(Job.vm_id).subquery('j')

            subquery2 = session.query(Job.vm_id, func.max(Job.state_date).label('last_job_date')).filter(Job.state.in_([JobState.FAILED, JobState.FINISHED, JobState.RUNNING])).group_by(Job.vm_id).subquery('i')

            results = session.query(Vm.vm_id.label('vm_id'), subquery1.c.jobs.label('job_count'), subquery2.c.last_job_date) \
                .outerjoin(subquery1, subquery1.c.vm_id == Vm.vm_id) \
                .outerjoin(subquery2, subquery2.c.vm_id == Vm.vm_id) \
                .filter(
                and_(
                    or_(
                        and_(  # case 1 - vm with jobs, check if vm has about half capacity available
                            Vm.cores - subquery1.c.cores >= Vm.cores / 2,
                            Vm.ram - subquery1.c.ram >= Vm.ram / 2
                        ),
                        and_(  # case 2 - vm with no jobs
                            subquery1.c.cores == None,
                            subquery1.c.ram == None,
                        )
                    ),
                    Vm.state.in_([VmState.READY])  # vm should be in state ready
                )
            ).all()

            if not results:
                return # no VM's to scalein

            deadline = datetime.utcnow() + timedelta(minutes=-10)

            vms_to_update = []
            mark_for_death_counter = 0
            for vm in results:
                if (vm[1] is None or vm[1] == 0) and (vm[2] is None or deadline > vm[2]):
                    vms_to_update.append(vm[0])
                elif deadline > vm[2]:
                    if mark_for_death_counter % 2 == 0:
                        vms_to_update.append(vm)
                    mark_for_death_counter += 1

            if len(vms_to_update) > 0:
                    session.commit()
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

            templates = dict(config.schedulerdomain.simplescaler.templates.as_dict()) # make a copy because we want to manipulate the list

            active_vms = query_bus.handle(query_factory.newRequestVms([VmState.NEW, VmState.PROVISION, VmState.READY]))

            provision_counter = 0
            for vm in active_vms:
                if vm.state in [VmState.NEW, VmState.PROVISION]:
                    cores -= vm.cores
                    ram -= vm.ram
                    provision_counter += 1
                # template = vm.vm_id.split('-')[0]
                # if template in templates:
                #     if 'spawned' in templates[template]:
                #         templates[template]['spawned'] += 1
                #     else:
                #         templates[template]['spawned'] = 1

            if provision_counter >= 6:
                # don't provision more than 6 VM's at the same time
                return

            # for template in list(templates): # make copy of list so that we can edit original
            #     if 'spawned' in templates[template] and templates[template]['spawned'] >= templates[template]['spawned-max']:
            #         del(templates[template]) # we already have the max amount of vms for this template

            # if not templates:
            #     return # max env size reached or no templates defined in config

            if cores <= 0 or cores < config.schedulerdomain.simplescaler.scaleoutmincoresneeded:
                return

            if ram <= 0 or ram < config.schedulerdomain.simplescaler.scaleoutminramneeded:
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

            #template = min(templates, key=lambda key: abs(templates[key]['distance'] - ram_per_core_needed))

            # scaleout by one instance
            cloudService = strongr.core.domain.clouddomain.CloudDomain.cloudService()
            cloudCommandFactory = strongr.core.domain.clouddomain.CloudDomain.commandFactory()
            cloudProviderName = config.clouddomain.driver
            profile = getattr(config.clouddomain, cloudProviderName).default_profile if 'profile' not in templates[template] else templates[template]['profile']
            deployVmsCommand = cloudCommandFactory.newDeployVms(names=[template + '-' + str(uuid.uuid4())], profile=profile, cores=templates[template]['cores'], ram=templates[template]['ram'])

            cloudCommandBus = cloudService.getCommandBus()

            logger.info('Deploying VM {0} cores={1} ram={2}GiB'.format(deployVmsCommand.names[0], templates[template]['cores'], templates[template]['ram']))

            cloudCommandBus.handle(deployVmsCommand)
