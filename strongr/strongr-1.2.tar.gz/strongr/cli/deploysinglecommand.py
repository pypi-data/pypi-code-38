from strongr.core import Core
from strongr.core.domain.clouddomain import CloudDomain
from .wrapper import Command

import uuid

class DeploySingleCommand(Command):
    """
    Deploys a VM in the cloud. A first step towards elasticity.

    deploy:single
    """
    def handle(self):
        cloudService = CloudDomain.cloudService()
        commandFactory = CloudDomain.commandFactory()

        cores = int(self.ask('How many processing cores should the VM have? (default 1): ', 1))
        ram = int(self.ask('How much memory in GiB should the VM have? (default 4): ', 4))
        name = self.ask('What is the name of the VM? (default generated): ', 'worker-' + str(uuid.uuid4()))

        if not (cores > 0 and ram > 0 and len(name) > 0):
            # TODO: put something sensible in here, this is just a placeholder
            self.error('Invalid input')
            return

        scaling_driver = Core.config().schedulerdomain.scalingdriver
        driver_config = getattr(Core.config().schedulerdomain, scaling_driver)
        profile = driver_config['default_profile']
        deployVmsCommand = commandFactory.newDeployVms(names=[name], profile=profile, cores=cores, ram = ram)

        commandBus = cloudService.getCommandBus()

        self.info('Deploying VM {0} cores={1} ram={2}GiB'.format(name, cores, ram))

        commandBus.handle(deployVmsCommand)
