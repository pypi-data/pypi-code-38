from rx import operators as ops
import rx
import re
import enum
import operator
from functools import reduce
from operator import itemgetter
from datetime import timedelta

from ...primitives.task import CLI
from ...taskstream.combinator import parallel
from ..base import Backend


class SlurmTaskState(enum.Enum):
    Canceled = "CA"
    Created = "PD"
    Running = "R"
    Suspend = "S"
    Completed = "CD"
    Failed = "F"
    TimeOut = "TO"
    NodeFault = "NF"


class SqueueIndex(enum.Enum):
    job_id = "JOBID"
    partition = "PARTITION"
    script = "NAME"
    user = "USER"
    state = "ST"
    time_used = "TIME"


class ScontrolIndex(enum.Enum):
    job_id = "JobId"
    exit_code = "ExitCode"
    run_time = "RunTime"
    time_limit = "TimeLimit"
    time_min = "TimeMin"
    submit_time = "SubmitTime"
    eligible_time = "EligibleTime"
    start_time = "StartTime"
    end_time = "EndTime"
    suspend_time = "SuspendTime"
    batch_host = "BatchHost"
    work_dir = "WorkDir"


class SlurmCLI(CLI):
    @classmethod
    def squeue(cls):
        def squeue_parser(squeue):
            squeue_splited = [line.split() for line in squeue]
            return rx.of([dict(zip(squeue_splited[0], i)) for i in squeue_splited[1:]])

        return super().cli("squeue").pipe(ops.flat_map(squeue_parser))

    @classmethod
    def sbatch(cls, script, dir):
        return super().cli(f"sbatch {script}", dir=dir)

    @classmethod
    def scancel(cls, job_id):
        return super().cli(f"scancel {job_id}")

    @classmethod
    def scontrol(cls, job_id):
        def aggregate(paires):
            tmp = {}
            for i in paires:
                tmp[i[0]] = i[1]
            return tmp

        return (
            super()
            .cli(f"scontrol show job {job_id}")
            .pipe(
                ops.map(lambda x: " ".join(x).split()),
                ops.map(lambda x: [i.split("=") for i in x]),
                ops.map(aggregate),
            )
        )


class Slurm(Backend):
    def __init__(self):
        pass

    @classmethod
    def queue(cls, *idx):
        """
        On-demand indexing of squeue.

        :usage: Slurm.queue(SqueueIndex.job_id, SqueueIndex.time_used).subscribe(print, print)
        :param idx: SqueueIndex typed indexing.
        :return: Observable of indexed squeue.

        >>> Slurm.queue(SqueueIndex.job_id, SqueueIndex.time_used).subscribe(print)
        >>> [('5750', '17:29'), ('5751', '17:29'), ('5752', '17:29'), ('5753', '17:29'),
        >>>  ('5754', '17:29'), ('5755', '17:29'), ('5756', '17:29'), ('5757', '17:29'),
        >>>  ('5758', '17:29'), ('5759', '17:29')]
        """

        def is_all_instance_of_SqueueIndex(l):
            return reduce(
                lambda x, y: operator.and_(x, y),
                [isinstance(i, SqueueIndex) for i in l],
                True,
            )

        if idx is tuple():
            return SlurmCLI.squeue()
        elif is_all_instance_of_SqueueIndex(idx):
            return SlurmCLI.squeue().pipe(
                ops.map(lambda x: [itemgetter(*[ii.value for ii in idx])(i) for i in x])
            )
        raise ValueError(f"Slurm.queue expect SqueueIndex type indexing, got {idx}")

    @classmethod
    def submit(cls, work_dir):
        return SlurmCLI.sbatch(script="run.sh", dir=work_dir)

    @classmethod
    def cancel(cls, task_id):
        return SlurmCLI.scancel(task_id)

    @classmethod
    def inspect(cls, task_id):
        return SlurmCLI.scontrol(task_id).pipe(
            ops.map(
                lambda x: itemgetter(*["JobId", "JobState", "RunTime", "WorkDir"])(x)
            )
        )

    @classmethod
    def overview(cls):
        """
        Overall information of backend for user to inspect.
        """

        def queue_inspecter(q):
            def timestr_to_seconds(t_str):
                t_l = t_str.split(":")
                if len(t_l) == 2:
                    return int(t_l[0]) * 60 + int(t_l[1])
                elif len(t_l) == 3:
                    return int(t_l[0]) * 3600 + int(t_l[1]) * 60 + int(t_l[2])
                else:
                    raise NotImplemented

            times = [i["TIME"] for i in q]

            content = {
                "jobs_on_exception": [i for i in q if i["ST"] not in ["R", "PD"]],
                "squeue": {
                    "length_of_queue": len(q),
                    "length_of_running": len([i for i in q if i["ST"] == "R"]),
                    "length_of_pending": len([i for i in q if i["ST"] == "PD"]),
                    "avg_running_time": str(
                        timedelta(seconds=sum(map(timestr_to_seconds, times)))
                        / len(times)
                    ),
                    "longest_running_time": str(
                        timedelta(seconds=max(list(map(timestr_to_seconds, times))))
                    ),
                },
            }

            return content

        return cls.queue().pipe(ops.map(queue_inspecter))

    @classmethod
    def purge(cls):
        return cls.queue(SqueueIndex.job_id).pipe(
            ops.map(lambda x: x[0]), ops.flat_map(cls.cancel)
        )

    # @classmethod
    # def is_overload(cls):
    #     pass

    @classmethod
    def completed(self):
        """
        Observable of completed queue.
        :return: A observable of completed queue along with task complete state and time used.

        >>> Slurm.completed().subscribe(print, print)
        >>> <rx.disposable.disposable.Disposable at 0x7f3acc0777b8>
        >>> ('5768', 'COMPLETED', '00:00:10')
        >>> ('5769', 'COMPLETED', '00:00:10')
        """

        def squeue_scanner(pre, nxt):
            last_running, _ = pre
            diff = [i for i in last_running if i not in nxt]
            return nxt, diff

        def check_on_diff(job_ids):
            return parallel([Slurm.inspect(i) for i in job_ids])

        _squeue = Slurm.queue(SqueueIndex.job_id).pipe(
            ops.reduce(lambda pre, nxt: pre + nxt)
        )

        return rx.interval(1.0).pipe(
            ops.flat_map(lambda _: _squeue),
            ops.scan(squeue_scanner, ([], [])),
            ops.map(lambda x: x[1]),
            ops.filter(lambda x: x != []),
            ops.flat_map(check_on_diff),
            ops.share(),
        )
