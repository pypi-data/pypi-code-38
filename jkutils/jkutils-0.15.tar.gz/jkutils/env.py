import logging
import os

from jkutils.zkCli import ZKClient, ConfigZKClient


class EnvZk:
    """
    管理项目的参数配置，环境变量
    """

    def __init__(self, zk_servers, service_name, host="", config_path="/entry/config/service"):
        if config_path:
            zk = ConfigZKClient(zk_servers, service_name, config_path)
        else:
            zk = ZKClient(zk_servers, service_name, host)

        zk.read_config()
        self._zk = zk
        self._conf_items = {}

    def init_conf(self, name, default=None, conftype=None, force=False, hash_log=None, pre_use=None):
        """
        初始化参数配置
        """
        conf = ConfItem(self._zk, name, default, conftype, force, hash_log, pre_use)
        self._conf_items[name] = conf
        return conf.value

    def __getitem__(self, key):
        """
        动态获取参数配置
        """
        try:
            return self._conf_items[key].value
        except KeyError:
            logging.error("getting conf failed. key [{}]".format(key))
            return None

    @property
    def config_data(self):
        return self._zk.config

    @property
    def zk_node_number(self):
        """
        zk 中当前节点后 7 位编号
        """
        return self._zk.zk_node_number

    def add_listener(self, func, key="default"):
        """
        添加配置变化的监听器

        def listener(config):
            pass
        
        ez = EnvZk()  
        ez.add_listener(listener)
        """
        self._zk.add_listener(func, key)


class ConfItem:
    """
    保存每一项配置的附属信息
    """

    def __init__(self, zk, name, default=None, conftype=None, force=False, hash_log=None, pre_use=None):
        self.zk = zk
        self.name = name
        self.default = default
        self.conftype = conftype
        self.force = force
        self.hash_log = hash_log
        self.pre_use = pre_use

    @property
    def value(self):
        """
        读取配置变量

        读取顺序: 环境变量 > zk > default
        """

        env = os.environ.get(self.name)
        if not env:
            env = self.zk.config.get(self.name, None)
            if env is None or env == "":  # 防止 env=False, env=0 等现象
                env = self.default

        if (env is None or env == "") and self.force:
            raise Exception("Not found env: <{}>".format(self.name))

        if self.conftype == bool and not isinstance(env, bool):
            env = False if str(env) in ("0", "false", "False") else True
        elif self.conftype:
            env = self.conftype(env)

        if self.hash_log:
            logging.info("{}: {}".format(self.name, self.hash_log(env)))
        else:
            logging.info("{}: {}".format(self.name, env))

        if self.pre_use and callable(self.pre_use):
            return self.pre_use(env)

        return env
