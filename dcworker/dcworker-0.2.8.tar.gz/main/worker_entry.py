from worker.worker_fsm import WorkerStateMachine
from worker.worker_start import *


def worker_entry(runtime: WorkerRuntime,
                 workdir: str,
                 toplevel_datadir: str,
                 port: int,
                 worker_uuid: str,
                 passcode: str,
                 gpu_id: str,
                 worker_info):

    worker = Worker(runtime.master_server(),
                    port,
                    workdir,
                    toplevel_datadir,
                    worker_uuid=worker_uuid,
                    worker_machine_type=runtime.get_worker_machine_type(),
                    gpu_id=gpu_id,
                    worker_info=worker_info,
                    passcode=passcode)

    worker_stm = WorkerStateMachine(worker, runtime)
    worker_stm.start()
