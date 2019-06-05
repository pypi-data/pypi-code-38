import strongr.core.gateways as gateways
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship, synonym

from strongr.schedulerdomain.model.vmstate import VmState

Base = gateways.Gateways.sqlalchemy_base()

class Vm(Base):
    __tablename__ = 'vms'

    vm_id = Column(String(64), primary_key=True)
    cores = Column(Integer)
    ram = Column(Integer)
    deadline = Column(DateTime())

    jobs = relationship('Job', back_populates='vm')

    _state = Column('state', Enum(VmState))

    # In classical SQL we would put a trigger to update this field with NOW() if the state-field is updated.
    # SQLAlchemy has no way to write triggers without writing platform-dependent SQL at the time of writing.
    # Instead we use a setter on the state-field, this setter updates the state_date as well.
    # The disadvantage of this solution is that other apps need to implement logic like this as well making
    # the solution less portable.
    state_date = Column(DateTime())

    @property
    def state(self):
        return self._state

    # update state_date-field as well when we update state-field
    @state.setter
    def state(self, value):
        self._state = value
        self.state_date = func.now()

    # create a synonym so that _state and state are considered the same field by the mapper
    state = synonym('_state', descriptor=state)
