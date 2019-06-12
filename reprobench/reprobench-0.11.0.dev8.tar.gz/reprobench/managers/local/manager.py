import atexit
import time
from multiprocessing import Pool

from sshtunnel import SSHTunnelForwarder
from loguru import logger
from tqdm import tqdm

from reprobench.core.worker import BenchmarkWorker
from reprobench.managers.base import BaseManager


class LocalManager(BaseManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_workers = kwargs.pop("num_workers")
        self.tunneling = kwargs.pop("tunneling")
        self.start_time = None
        self.workers = []

    def exit(self):
        for worker in self.workers:
            worker.terminate()
            worker.join()

        logger.info(f"Total time elapsed: {time.perf_counter() - self.start_time}")

    def prepare(self):
        atexit.register(self.exit)
        self.start_time = time.perf_counter()
        if self.tunneling is not None:
            self.server = SSHTunnelForwarder(
                self.tunneling["host"],
                remote_bind_address=("127.0.0.1", self.tunneling["port"]),
                ssh_pkey=self.tunneling["key_file"],
            )
            self.server.start()
            self.server_address = f"tcp://127.0.0.1:{self.server.local_bind_port}"
            logger.info(f"Tunneling established at {self.server_address}")

    @staticmethod
    def spawn_worker(server_address):
        worker = BenchmarkWorker(server_address)
        worker.run()

    def spawn_workers(self):
        self.pool = Pool(self.num_workers)
        jobs = (self.server_address for _ in range(self.pending))
        self.pool_iterator = self.pool.imap_unordered(self.spawn_worker, jobs)
        self.pool.close()

    def wait(self):
        progress_bar = tqdm(desc="Executing runs", total=self.pending)
        for _ in self.pool_iterator:
            progress_bar.update()
        progress_bar.close()
        self.pool.join()

        if self.tunneling is not None:
            self.server.stop()
