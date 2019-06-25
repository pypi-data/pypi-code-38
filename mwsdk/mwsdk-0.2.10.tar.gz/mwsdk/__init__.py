from .kong import Kong,KongError
from mwutils.mw_consul import AgentConf,reg_service,dereg_service
from .auth import Auth,AuthError
from .rightmanage import Rightmanage,Rightmanage_inner,AIORightmanage_inner

# 註冊服務到consul
reg_service = reg_service
dereg_service = dereg_service

# # 本機consul agent的配置
consul_agent_conf = AgentConf()




