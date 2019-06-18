from restclients_core.util.decorators import use_mock
from uw_hrp.dao import HRP_DAO

fdao_hrp_override = use_mock(HRP_DAO())
