import os
from core.request import Request
from core.proxies import Proxies
from core.database import Database
from core.thread_pool import ThreadPool


class Basic:
    """
    contains basic functions that will be inherited
    """
    proxy_type = None
    conn_type = 1

    def __init__(self, only_ms=True, db_config=None):
        # necessary variables
        self.threads = {}

        # database settings
        self.db_type = 'ms'
        self.db_type2 = 'ora'
        self.conn_type = self.conn_type
        if db_config is None:
            self.database_config = r'C:\Users\{}\Documents\database.config'.format(os.getlogin())
        else:
            self.database_config =  db_config
        self.database = self.create_db_engine()
        if only_ms is False:
            self.database2 = self.create_db_engine(db=2)


        # proxy lists settings
        self.tor_view = 'v_tor_list'
        self.proxy_view = 'v_proxy_list'
        self.proxy_https = 'v_proxy_list_https'

        self.proxy_type = self.proxy_type
        self.proxy_switch()
        self.new_ip = {}

    @staticmethod
    def create_pool(workers=10):
        return ThreadPool(workers)

    def create_db_engine(self, db=1, conf_path=None):
        db_type = self.db_type
        if db != 1:
            db_type = self.db_type2
        Database.db_type = db_type
        if conf_path is None:
            if self.conn_type != 1:
                return Database(self.database_config, conn_type=self.conn_type)
            return Database(self.database_config)
        else:
            if self.conn_type != 1:
                return Database(conf_path, conn_type=self.conn_type)
            return Database(conf_path)

    def proxy_switch(self):
        if self.proxy_type is 1:
            # public proxies
            self.proxy_type = 2
            self.proxies = Proxies(self.database, self.proxy_view, ipname='proxy_ip', portname='proxy_port', conn_type=self.conn_type)

        if self.proxy_type is 2:
            # tor proxies
            self.proxy_type = 1
            self.proxies = Proxies(self.database, self.tor_view, hostip='ipv4', conn_type=self.conn_type)

        if self.proxy_type is None:
            # public proxies
            self.proxy_type = 2
            self.proxies = Proxies(self.database, self.proxy_view, ipname='proxy_ip', portname='proxy_port', conn_type=self.conn_type)

        if self.proxy_type == 3:
            # public proxies
            self.proxy_type = 3
            self.proxies = Proxies(self.database, self.proxy_https, ipname='proxy_ip', portname='proxy_port', conn_type=self.conn_type)

    def new_request(self, thread_number, new=False):
        r = Request()
        r.proxy_type = self.proxy_type
        if new is False:
            r = self.proxies.set_proxy(r, thread_number)
        if new is True:
            r = self.proxies.set_proxy(r, thread_number, new=True)
        self.threads.update({thread_number: r})
        self.new_ip.update({thread_number: True})