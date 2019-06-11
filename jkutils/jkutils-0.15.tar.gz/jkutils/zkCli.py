import json
import logging

from kazoo.client import KazooClient


class ZKClient:
    def __init__(self, zk_servers, service_name, host):
        self._listener = {}
        self.config = None
        self.zk = KazooClient(zk_servers)
        self.zk.start()

        self.service_name = service_name
        self.serve_path = "/entry/service/{}/node".format(service_name)
        self.zk.ensure_path(self.serve_path)
        node_path = self.zk.create(self.serve_path + "/server", host.encode(), ephemeral=True, sequence=True)
        self.zk_node_number = str(node_path)[-7:]
        self.config_path = "/entry/config/service/{}".format(self.service_name)
        self.zk.DataWatch(self.config_path, self.read_config)

    def read_config(self, *args):
        logging.info("ZKClient: Parameter configuration updated")
        self.zk.ensure_path("/entry/config/service")
        if not self.zk.exists(self.config_path):
            self.zk.create(self.config_path, json.dumps({}).encode())
        self.config = json.loads(self.zk.get(self.config_path)[0].decode())

        # 推送到所有监听器
        for _, func in self._listener.items():
            func(self.config)

    def update_config(self, config):
        self.zk.set(self.config_path, json.dumps(config).encode())

    def add_listener(self, func, key="default"):

        if func is None and key in self._listener:
            del self._listener[key]
            return

        if not callable(func):
            raise Exception("'func' must be callable!")

        self._listener[key] = func


class ConfigZKClient:
    def __init__(self, zk_servers, service_name, config_path):
        self._listener = {}
        self.config = None
        self.zk = KazooClient(zk_servers)
        self.zk.start()
        self.config_path = config_path
        self.server_config_path = "{}/{}".format(config_path, service_name)
        self.zk.ensure_path(self.config_path)
        self.zk.ensure_path(self.server_config_path + "/server/")
        node_path = self.zk.create(self.server_config_path + "/server/", "".encode(), ephemeral=True, sequence=True)
        self.zk_node_number = str(node_path)[-7:]
        self.zk.DataWatch(self.server_config_path, self.read_config)

    def read_config(self, *args):
        logging.info("ConfigZKClient: Parameter configuration updated")
        self.zk.ensure_path(self.config_path)
        if not self.zk.exists(self.server_config_path):
            self.zk.create(self.server_config_path, json.dumps({}).encode())
        self.config = json.loads(self.zk.get(self.server_config_path)[0].decode())

        # 推送到所有监听器
        for _, func in self._listener.items():
            func(self.config)

    def update_config(self, config):
        self.zk.set(self.server_config_path, json.dumps(config).encode())

    def add_listener(self, func, key="default"):

        if func is None and key in self._listener:
            del self._listener[key]
            return

        if not callable(func):
            raise Exception("'func' must be callable!")

        self._listener[key] = func


class RegisterZkClient:

    def __init__(self, zk_servers, ip, service_name, serve_path="/entry/service", node_name="server"):
        self.zk = KazooClient(zk_servers)
        self.zk.start()

        self.serve_path = "{}/{}/node".format(serve_path, service_name)
        self.node_name = node_name
        self.zk.ensure_path(self.serve_path)
        self.ip = ip

    def register(self):
        self.zk.create("{}/{}".format(self.serve_path, self.node_name), self.ip.encode(), ephemeral=True, sequence=True)
