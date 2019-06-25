from unicon.plugins.generic import ServiceList
from unicon.bases.routers.connection import BaseSingleRpConnection
from unicon.plugins.generic.statemachine import GenericSingleRpStateMachine
from unicon.plugins.generic import GenericSingleRpConnectionProvider
from unicon.plugins.generic.settings import GenericSettings

class IosServiceList(ServiceList):
    def __init__(self):
        super().__init__()


class IosSingleRpConnection(BaseSingleRpConnection):
    os = 'ios'
    chassis_type = 'single_rp'
    state_machine_class = GenericSingleRpStateMachine
    connection_provider_class = GenericSingleRpConnectionProvider
    subcommand_list = IosServiceList
    settings = GenericSettings()
