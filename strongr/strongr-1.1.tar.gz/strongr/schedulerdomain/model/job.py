import strongr.core.gateways as gateways
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, DateTime, func, LargeBinary, Text, Boolean
from sqlalchemy.orm import relationship, synonym

from strongr.schedulerdomain.model import JobState

Base = gateways.Gateways.sqlalchemy_base()

class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(String(64), primary_key=True)
    cores = Column(Integer)
    ram = Column(Integer)
    script = Column(Text)
    image = Column(Text)
    scratch = Column(Boolean)

    _secrets = Column(Text)

    vm_id = Column(String(255), ForeignKey('vms.vm_id'))
    vm = relationship('Vm', back_populates='jobs')

    return_code = Column(Integer)

    stdout = Column('stdout', LargeBinary(length=52428800)) # we should update this to point to a file at some point as it will bloat the database pretty quickly

    _state = Column('state', Enum(JobState))

    @property
    def secrets(self):
        return self._secrets.split('\n')

    # update state_date-field as well when we update state-field
    @secrets.setter
    def secrets(self, array_of_secrets):
        self._secrets = '\n'.join(array_of_secrets)

    # create a synonym so that _state and state are considered the same field by the mapper
    secrets = synonym('_secrets', descriptor=secrets)

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



    # # use zlib / gzip compression for stdout
    # @property
    # def stdout(self):
    #     return zlib.decompress(self._stdout)
    #
    # @stdout.setter
    # def stdout(self, value):
    #     self._stdout = zlib.compress(value, 9)
    #
    # # create a synonym so that _stdout and stdout are considered the same field by the mapper
    # stdout = synonym('_stdout', descriptor=stdout)
