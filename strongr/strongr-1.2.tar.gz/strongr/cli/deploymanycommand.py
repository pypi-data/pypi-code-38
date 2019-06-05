from strongr.core import Core
from strongr.core.domain.clouddomain import CloudDomain
from .wrapper import Command

import uuid

class DeployManyCommand(Command):
    """
    Deploys VM's in the cloud in a parallel way. A first step towards elasticity.

    deploy:many
    """
    def handle(self):
        cloudService = CloudDomain.cloudService()
        commandFactory = CloudDomain.commandFactory()

        cores = int(self.ask('How many processing cores should the VM\'s have? (default 1): ', 1))
        ram = int(self.ask('How much memory in GiB should the VM\'s have? (default 4): ', 4))
        amount = int(self.ask('How many VM\'s should be deployed? (default 2)', 2))

        if not (cores > 0 and ram > 0 and amount > 0):
            # TODO: put something sensible in here, this is just a placeholder
            self.error('Invalid input')
            return

        deployVmNameList = []
        while amount > 0:
            deployVmNameList.append('worker-' + str(uuid.uuid4()))
            amount -= 1

        scaling_driver = Core.config().schedulerdomain.scalingdriver

        profile = getattr(Core.config().schedulerdomain, scaling_driver).default_profile
        deployVms = commandFactory.newDeployVms(names=deployVmNameList, profile=profile, cores=cores, ram=ram)
        commandBus = cloudService.getCommandBus()

        self.info('Deploying {0} VM\'s with cores={1} ram={2}GiB'.format(len(deployVmNameList), cores, ram))

        commandBus.handle(deployVms)
