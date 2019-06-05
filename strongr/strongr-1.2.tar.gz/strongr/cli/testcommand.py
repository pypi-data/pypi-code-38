# from sqlalchemy import func, and_, or_
#
# from strongr.schedulerdomain.model import Job, JobState, VmState, Vm
from strongr.schedulerdomain.model.scalingdrivers.surfhpccloudscaler import SurfHpcScaler
from .wrapper import Command
#
# import strongr.core.gateways

import strongr.core.domain.schedulerdomain

class TestCommand(Command):
    """
    Runs experimental testcode

    test:run
    """
    def handle(self):
        s = SurfHpcScaler(config=dict(strongr.core.Core.config().schedulerdomain.as_dict()[strongr.core.Core.config().schedulerdomain.scalingdriver]))
        s.scaleout(None)
