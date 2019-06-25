import logging
import sys

from flask import Flask
from flask_cors import *

import config

log = logging.getLogger('Ficus')

log.info("=======服务启动开始======")
app = Flask(__name__)
# 设置跨域
CORS(app, supports_credentials=True)

#读取本地配置文件
from config.BootstrapPropertyLoader import load_properties_after_started, init_from_yaml_property,init_from_environ_property
init_from_yaml_property(sys.argv[0])
# 尝试从环境变量中获取 bootstrap里面的信息
init_from_environ_property()

log.info("服务启动,完成本地yaml配置文件读取")

# 注册信息到eureka中
from py_eureka_client import eureka_client
eureka_client.init(eureka_server=config.eureka_default_zone,
                   app_name=config.application_name,
                   # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                   instance_host=config.server_ip or config.find_host_ip(),
                   instance_port=config.server_port or 5000,
                   # 调用其他服务时的高可用策略，可选，默认为随机
                   ha_strategy=eureka_client.HA_STRATEGY_STICK,
                   status_page_url="/actuator/info",
                   health_check_url="/actuator/health",
                   renewal_interval_in_secs=2,
                   duration_in_secs=6)

log.info("服务启动,完成注册中心注册及心跳")

load_properties_after_started(sys.argv[0])

log.info("服务启动,完成配置中心配置文件读取")

# 这一行不能去掉,目的是引入flask的endpoints,并且位置需要在 app = Flask(__name__) 后面
# 引入views
from remote import remote

app.register_blueprint(remote, url_prefix='/')

log.info("服务启动,完成flask框架启动")

# 先加载registry.yml
import registry
registry.load_registry_properties(sys.argv[0], "registry.yml")

# 加载规则引擎的配置
from rule_engine import RuleEngineInitialize
RuleEngineInitialize.initialize_from_remote()
log.info("服务启动,完成规则引擎的初始化")

# 预先加载根目录下的这个模块,这样才能在程序启动后,自动注册执行器
try:
    import handlers
except:
    pass
log.info("服务启动,完成处理器的预加载")

# 程序启动后,判断是否需要注册执行器
from registry.LoadOnRegistryLoader import registry_after_started
registry_after_started()

log.info("服务启动,完成处理器的注册")

from schedule.utils.log.TaskLogCleanScheduler import TaskLogCleanScheduler
log_cleaner = TaskLogCleanScheduler()
log_cleaner.start()
log.info("服务启动,完成日期清理线程的启动")

log.info(f"服务启动:{config.server_ip or config.find_host_ip()}:{config.server_port or 5000}")
log.info("======服务启动完毕======")