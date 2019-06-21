
class ThreadData:
    pass


class Proxies:

    def __init__(self, database, view_name=None, ipname='ip', portname='port', hostip=None, conn_type=1):
        """ database = provide already established database instance
            view_name = name of view that contains proxy and port data
            ipname = column name in view that contains ip
            portname = column name in view that contains port
            hostip = column name in view that contains hostip (this is for tor only)
        """
        self.ipname = ipname
        self.portname = portname
        self.database = database
        self.view_name = view_name
        self.proxy_list = None
        self.host_ip = hostip
        self.blocked = []
        self.threads = {}
        self.conn_type = conn_type
        self.update_proxy_list()

    def update_proxy_list(self):
        args = {'tablename': self.view_name}
        if self.database.db_type == 'MsSql':
            args.update({'view': True})
        self.proxy_list = iter(self.database.select(**args))

    def set_proxy(self, request, thread, new=False):
        """request = provide created instance of Request()"""
        while True:
            # get thread data storage
            search_thread = self.threads.get(thread)
            proxy_data = next(self.proxy_list, None)

            if proxy_data is None:
                self.update_proxy_list()
                # if thread data storage exists then reset blocked list
                if search_thread is not None:
                    setattr(search_thread, 'blocked', [])
                continue

            ip = proxy_data.get(self.ipname)
            port = proxy_data.get(self.portname)
            ipv4 = proxy_data.get(self.host_ip)

            if search_thread is None:
                thread_storage = ThreadData()
                attrs = {'ip': ip ,
                         'ipv4': ipv4,
                         'port': port,
                         'blocked': []}
                for k, v in attrs.items():
                    setattr(thread_storage, k, v)
                self.threads.update({thread: thread_storage})

            search_thread = self.threads.get(thread)
            if new is True:
                old_ip = getattr(search_thread, 'ip')
                blocked = getattr(search_thread, 'blocked')
                blocked.append(old_ip)
                setattr(search_thread,'blocked', blocked)
                if ip in blocked:
                    continue
                setattr(search_thread, 'ip', ip)
                setattr(search_thread, 'ipv4', ipv4)
                setattr(search_thread, 'port', port)

            # update request variables
            if self.host_ip is not None:
                request.ip = getattr(search_thread, self.host_ip)
            else:
                request.ip = ip
            request.port = port
            return request





