import rx
from rx import operators as ops
import json
import requests
import operator
from functools import reduce

# from dxl.picluster.database.transactions import deserialization
# from .base import SlurmOp, SlurmTaskState
from ..base import Backend

from ...database.model.schema import Task
from ...config.slurm import SlurmConfig


class Slurm:
    def __init__(self, ip, port, api_version, *args, **kwargs):
        self.ip = ip
        self.port = port
        self.api_version = api_version

    def __repr__(self):
        return f"Backend(type=Slurm, ip={self.ip}, port={self.port}, api_version={self.api_version})"

    def url(self, *arg, **kwargs):
        url = f"http://{self.ip}:{self.port}/api/v{self.api_version}/slurm/{arg[0]}?"
        kvs = []
        for k, v in kwargs.items():
            kvs.append(f"{k}={v}")
        return url + "&".join(kvs)

    def _squeue(self):
        response = requests.get(self.url(SlurmOp.squeue.value)).text
        return json.loads(response)

    def _scancel(self, id: int):
        if id is None:
            raise ValueError
        return requests.delete(self.url(SlurmOp.scancel.value, job_id=id)).text

    def _scontrol(self, id: int):
        def query(observer, scheduler):
            try:
                result = requests.get(
                    self.url(SlurmOp.scontrol.value, job_id=id)
                ).json()
                observer.on_next(result["job_state"])
                observer.on_completed()
            except:
                pass

        return rx.create(query)

    def queue(self):
        return rx.interval(1.0).pipe(ops.map(lambda _: self._squeue()), ops.share())

    def completed(self):
        def squeue_scanner(last, current):
            last_running, _ = last
            result = (current, [i for i in last_running if i not in current])
            return result

        complete_queue = rx.interval(1.0).pipe(
            ops.map(lambda _: self._squeue()),
            ops.map(lambda l: [i["job_id"] for i in l]),
            ops.scan(squeue_scanner, ([], [])),
            ops.map(lambda x: x[1]),
            ops.filter(lambda x: x != []),
        )
        return complete_queue

    def submit(self, task: "Task"):
        def _sbatch():
            work_dir = task.workdir
            file = task.script

            arg = file
            _url = self.url(SlurmOp.sbatch.value, arg=arg, file=file, work_dir=work_dir)
            result = requests.post(_url).json()

            try:
                result = int(result["job_id"])
            except Exception as e:
                print(
                    f"SLurm submit Error!, ***{e}*** sbatch error, expected slurm_id, got {result}"
                )

            return result

        return _sbatch()

    def cancel(self, task: "Task"):
        if isinstance(task, Task):
            response = self._scancel(task.id_on_backend)
        elif isinstance(task, int):
            response = self._scancel(task)

        return str(response)

    def is_overload(self):
        def _is_overload(squeue):
            if len(squeue):
                tmp = [i["status"] == SlurmTaskState.Created.value for i in squeue]
                return reduce(operator.or_, tmp)
            if not len(squeue):
                return False

        return self.queue().pipe(ops.map(_is_overload))

    def inspect(self, task):
        pass


def squeue_scanner(last, current):
    last_running, _ = last
    result = (current, [i for i in last_running if i not in current])
    return result


SlurmSjtu = Slurm(
    ip=SlurmConfig.RestSlurm_IP,
    port=SlurmConfig.RestSlurm_Port,
    api_version=SlurmConfig.Api_Version,
)
