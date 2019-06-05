import uuid

import strongr.core
import logging

class EnsureMinAmountOfNodesHandler(object):
    def __call__(self, command):
        config = strongr.core.Core.config()
        templates = config.schedulerdomain.simplescaler.templates.as_dict()
        logger = logging.getLogger('schedulerdomain.' + self.__class__.__name__)

        cloudQueryBus = strongr.core.domain.clouddomain.CloudDomain.cloudService().getQueryBus()
        cloudQueryFactory = strongr.core.domain.clouddomain.CloudDomain.queryFactory()

        machines = cloudQueryBus.handle(cloudQueryFactory.newListDeployedVms())

        template_counters = {}
        machines_needed = {}
        for machine in machines:
            for template_name in templates:
                if machine.startswith(template_name + '-'):
                    if template_name in template_counters:
                        template_counters[template_name] += 1
                    else:
                        template_counters[template_name] = 1
                    break

        for template_name in templates:
            if template_name in template_counters and template_counters[template_name] < templates[template_name]['spawned-min']:
                machines_needed[template_name] = templates[template_name]['spawned-min'] - template_counters[template_name]
            else:
                machines_needed[template_name] = templates[template_name]['spawned-min']


        if len(machines_needed) > 0:
            logger.info('Machines needed: {}'.format(machines_needed))
            for machine in machines_needed:
                cloudService = strongr.core.domain.clouddomain.CloudDomain.cloudService()
                commandFactory = strongr.core.domain.clouddomain.CloudDomain.commandFactory()
                cloudProviderName = config.clouddomain.driver
                profile = getattr(config.clouddomain, cloudProviderName).default_profile if 'profile' not in templates[machine] else templates[machine]['profile']
                names = []
                for i in range(0, machines_needed[machine]):
                    names.append(machine + '-' + str(uuid.uuid4()))

                deployVmsCommand = commandFactory.newDeployVms(names=names, profile=profile, cores=templates[machine]['cores'], ram=templates[machine]['ram'])

                commandBus = cloudService.getCommandBus()

                logger.info('Deploying VMs {0} cores={1} ram={2}GiB'.format(names, templates[machine]['cores'], templates[machine]['ram']))

                commandBus.handle(deployVmsCommand)
        else:
            logger.info('No aditional machines needed!')
