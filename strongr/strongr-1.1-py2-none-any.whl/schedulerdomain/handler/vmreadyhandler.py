import strongr.core.gateways
import strongr.core
from strongr.schedulerdomain.model import Vm, VmState
from strongr.schedulerdomain.model.scalingdrivers import ScalingDriver


class VmReadyHandler(object):
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()

        deadline = ScalingDriver.scaling_driver().get_vm_max_age(command.vm_id)

        session.query(Vm).filter(Vm.vm_id == command.vm_id).update({Vm.state: VmState.READY, Vm.deadline: deadline}, synchronize_session='fetch')
