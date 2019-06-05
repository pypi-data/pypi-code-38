import strongr.core.gateways
from strongr.schedulerdomain.model import Vm, VmState

class VmNewHandler(object):
    def __call__(self, command):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        vm = Vm()
        vm.vm_id = command.vm_id
        vm.state = VmState.NEW
        vm.cores = command.cores
        vm.ram = command.ram

        session.add(vm)
