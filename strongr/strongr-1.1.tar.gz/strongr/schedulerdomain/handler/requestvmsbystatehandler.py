import strongr.core.gateways
from strongr.schedulerdomain.model import Vm


class RequestVmsByStateHandler(object):
    def __call__(self, query):
        session = strongr.core.gateways.Gateways.sqlalchemy_session()
        return session.query(Vm).filter(Vm.state.in_(query.states)).all()
