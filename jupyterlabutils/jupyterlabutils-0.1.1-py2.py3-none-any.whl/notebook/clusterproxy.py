from .forwarder import Forwarder
from .utils import get_proxy_url, get_hostname
import ipaddress
import logging
from dask.distributed import Client


def _remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s


class ClusterProxy(object):
    """Provides a proxy service to map a local port to a worker node's
    dashboard, which should be on its "dashboard" service.

    This allows us to proxy to the worker even though the k8s network is not
    accessible externally.

    It must be created with an instance of a dask.distributed.Client
    as its argument.
    """
    client = None
    cluster = None
    ioloop = None
    workers = {}

    def __init__(self, client):
        if not isinstance(client, Client):
            estr = "'client' argument must be dask.distributed.Client!"
            raise RuntimeError(estr)
        self.client = client
        self.logger = logging.getLogger(__name__)
        self.cluster = client.cluster
        self.ioloop = client.io_loop
        self.scheduler_url = None
        port = client.cluster.scheduler.identity()["services"].get("dashboard")
        if port:
            self.scheduler_url = get_proxy_url(port) + "/status"
        self.refresh_workers()

    def refresh_workers(self):
        """Rebuild current worker map from actual state.
        """
        current_workers = self.cluster.scheduler.identity().get('workers')
        current_workerlist = list(current_workers.keys())
        removed_workers = []
        for worker_id in self.workers:
            if worker_id not in current_workerlist:
                # Get rid of removed workers
                self._remove_worker_proxy(worker_id)
                removed_workers.append(worker_id)
        for worker_id in removed_workers:
            del self.workers[worker_id]
        for worker_id in current_workerlist:
            if worker_id not in self.workers:
                worker_record = current_workers[worker_id]
                self.workers[worker_id] = self._create_worker_proxy(
                    worker_record)
            # Otherwise it hasn't changed.

    def _remove_worker_proxy(self, worker_id):
        worker = self.workers.get(worker_id)
        if not worker:
            return
        forwarder = worker["forwarder"]
        if not forwarder:
            return
        forwarder.stop()

    def _create_worker_proxy(self, worker_record):
        host = worker_record["host"]
        ipaddr = ipaddress.ip_address(host)
        port = worker_record["services"].get("dashboard")
        if not port:
            return None
        if ipaddr.is_loopback:
            proxy = None
            local_port = port
        else:
            proxy = Forwarder(host, port, ioloop=self.ioloop)
            proxy.start()
            local_port = proxy.get_port()
        url = get_proxy_url(local_port) + "/main"
        worker = {"forwarder": proxy,
                  "url": url,
                  "local_port": local_port}
        return worker

    def get_proxies(self, workers):
        """Returns a dict of worker endpoints as keys, mapped to a dict
        containing the worker proxy url and local port it's mapped to.
        """
        rval = {}
        if not workers:
            workers = list(self.workers.keys())
        if workers:
            if type(workers) is str:
                workers = [workers]
        for worker in workers:
            if not worker:
                continue
            for val in ["url", "local_port"]:
                rval[worker][val] = self.workers[worker].get(val),
        return rval

    def __repr__(self):
        s = "<ClusterProxy {name}>".format(name=get_hostname())
        s += "\n  Scheduler: {url}".format(url=self.scheduler_url)
        self.refresh_workers()
        sw = self.workers
        if sw:
            s = s+"\n  Workers:"
        for worker in sw:
            s += "\n    {worker}: {url}".format(worker=worker,
                                                url=sw[worker]["url"])
        return s

    def _repr_html_(self):
        s = "<h4>&lt;ClusterProxy {name}&gt;</h4>".format(name=get_hostname())
        s += " <b>Scheduler: <a href=\'{u}\'>{u}</a></b>".format(
            u=self.scheduler_url)
        if len(self.workers) > 0:
            s += "<h4>Workers</h4>\n<dl>\n"
            self.refresh_workers()
            sw = self.workers
            for worker in sw:
                s += "<dt><b>{w}</b></dt>".format(w=worker)
                s += "<dd><a href=\'{u}\'>{u}</href></a></dd>\n".format(
                    u=sw[worker]["url"])
            s += "</dl>"
        return s
