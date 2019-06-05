from strongr.core.gateways import Gateways
from strongr.core.domain.schedulerdomain import SchedulerDomain
from strongr.core.domain.restdomain import RestDomain
from strongr.core.domain.secretdomain import SecretDomain

from .wrapper import Command

class MakeDbCommand(Command):
    """
    Create empty database

    database:create
    """
    def handle(self):
        services = [
            SchedulerDomain.schedulerService(),
            RestDomain.oauth2Service(),
            SecretDomain.secret_service()
        ]

        for service in services:
            service.register_models()


        db = Gateways.sqlalchemy_engine()
        metadata = Gateways.sqlalchemy_base().metadata
        metadata.create_all(db)

        # from sqlalchemy.exc import IntegrityError
        # try:
        #     from strongr.schedulerdomain.model import Vm, VmState, Job, JobState
        #     vm = Vm()
        #     vm.cores = 4
        #     vm.ram = 32
        #     vm.vm_id = "7163a8cc-8d7d-409e-9360-52e6f6fe5b8a"
        #     vm.state = VmState.NEW
        #
        #     session = Gateways.sqlalchemy_session()
        #     session.add(vm)
        #     session.commit()
        # except IntegrityError:
        #     pass # continue when record already exists, we don't really care
        #
        # query_factory = SchedulerDomain.queryFactory()
        # query_bus = SchedulerDomain.schedulerService().getQueryBus()
        #
        # print(query_bus.handle(query_factory.newFindNodeWithAvailableResources(1, 1)))
