import strongr.core.gateways
from strongr.schedulerdomain.model import Vm, VmState

class VmCreatedHandler(object):
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        session.query(Vm).filter(Vm.vm_id == command.vm_id).update({Vm.state: VmState.PROVISION}, synchronize_session='fetch')
