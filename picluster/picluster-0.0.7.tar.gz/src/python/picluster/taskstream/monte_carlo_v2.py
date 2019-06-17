from ..database.model.schema import Task
from ..primitives.task import TASK, TaskUtils

# from .combinator import concate

from ..primitives.resources import FileResource
from .cli_tasks import CLI
from pathlib import Path
import rx
import json
from rx import operators as ops
from .combinator import parallel
from ..backend.slurm.slurm_v2 import Slurm


class MonteCarloBase(TASK):
    """
    Usage:
    >>> mc_dummy = MonteCarloBase(target_mac="/mnt/users/nini/simu_20190605/xcat/mct_xcat_1e7_150z_1_5s.mac",
    >>>                           resources=FileResource(
    >>>                                         "/mnt/deployment/monte_carlo_simu_common_resources",
    >>>                                         "/mnt/users/nini/simu_20190605/xcat/data"
    >>>                                     ),
    >>>                           result_dir="simu_90",
    >>>                           nb_splits=90,
    >>>                           spec={"commit":"test for xcat"})

    >>> mc_dummy.observable().subscribe(print,print)
    """

    def __init__(
        self,
        target_mac,
        nb_splits,
        spec={},
        result_dir="simu_result",
        resources=FileResource("/mnt/deployment/monte_carlo_simu_common_resources"),
    ):
        self.target_mac = Path(target_mac)
        self.result_dir = result_dir
        self.nb_splits = nb_splits
        self.sub_pattern = lambda i: f"sub.{i}"
        self.resources = resources.content
        self.spec = spec
        self.sub_task_dirs = None
        self.ids_on_backend = []

    @property
    def work_dir(self):
        return self.target_mac.parent

    # @property
    # def task(self):
    #     return Task(hash=self.hash, workdir=self.work_dir, spec=self.spec)

    @property
    def master_task_dir(self):
        return self.work_dir / self.result_dir

    def pre_create(self):
        """
        Create a dedicated work directory for a mac with sematic file name,
        by making a new directory with the same name as mac.
        Or check if a dedicated work directory exists.

        :return: Observale of target mac Url.
        """

        if self.target_mac.name != "main.mac":
            previous_target_mac = self.target_mac
            new_target_mac = (
                self.target_mac.parent
                / self.target_mac.name.rstrip(Path(self.target_mac.name).suffix)
                / "main.mac"
            )

            def update_target_mac(*args):
                self.target_mac = new_target_mac
                return self.target_mac

            if not new_target_mac.parent.is_dir():
                return rx.of(new_target_mac.parent).pipe(
                    ops.flat_map(CLI.mkdir),
                    ops.flat_map(lambda _: CLI.cp(previous_target_mac, new_target_mac)),
                    ops.map(update_target_mac),
                )
            else:
                update_target_mac()
                return rx.of(self.target_mac)
        else:
            return rx.of(self.target_mac)

    def on_create(self):
        def get_subdirs(work_dir):
            self.sub_task_dirs = rx.from_list(
                [Path(work_dir) / self.sub_pattern(i) for i in range(self.nb_splits)]
            )
            return self.sub_task_dirs

        def load_resources(work_dir):
            return parallel(
                [CLI.cp(r, work_dir) for r in self.resources]
                + [CLI.cp(self.target_mac, Path(work_dir) / "main.mac")]
            )

        def check_on_create(load_count):
            supposed_count = (len(self.resources) + 1) * self.nb_splits
            if load_count == supposed_count:
                return True
            else:
                raise BrokenPipeError(
                    f"Pipe error on create: {supposed_count} transactions supposed to be made, while seen {load_count}"
                )

        return rx.of(self.master_task_dir).pipe(
            ops.flat_map(CLI.mkdir),
            ops.flat_map(get_subdirs),
            ops.flat_map(CLI.mkdir),
            ops.flat_map(load_resources),
            ops.count(),
            ops.map(check_on_create),
            ops.flat_map(lambda _: self.sub_task_dirs),
        )

    def on_submit(self):
        def _on_subscribe(msg):
            self.ids_on_backend.append(int(msg[0][20:]))
            return msg

        def dump_meta(x):
            task_meta_url = self.master_task_dir / (self.hash + ".json")
            task_meta = {
                "hash": self.hash,
                "task_mac": str(self.target_mac),
                "number_of_split": self.nb_splits,
                "result_dir": str(self.master_task_dir),
                "spec": self.spec,
                "tags": self.work_dir.name.split("_"),
            }

            with open(task_meta_url, "w") as f:
                json.dump(task_meta, f)

            return x

        return self.sub_task_dirs.pipe(
            ops.flat_map(Slurm.submit),
            ops.flat_map(_on_subscribe),
            ops.last(),
            ops.map(dump_meta),
            ops.map(lambda _: self.ids_on_backend),
        )

    def on_error(self):
        pass

    def on_complete(self):
        def _extract_result():
            # TODO workdir should be able to purge after run, only result is needed.
            pass

        def _clean_work_directory():
            pass

        pass

    def roll_back(self):
        def reset_ids_on_backend(x):
            self.ids_on_backend = []
            return x

        return rx.from_list(self.ids_on_backend).pipe(
            ops.flat_map(Slurm.cancel),
            ops.last(),
            ops.map(reset_ids_on_backend),
            ops.flat_map(lambda _: CLI.rm(self.work_dir / self.result_dir)),
        )

    @property
    def hash(self):
        sroted_list_of_resource_hash = sorted(
            [TaskUtils.file_hash(r) for r in self.resources]
            + [TaskUtils.file_hash(self.target_mac)]
        )
        return TaskUtils.string_hash("".join(sroted_list_of_resource_hash))

    def observable(self):
        return (
            self.pre_create()
            .pipe(ops.last(), ops.flat_map(lambda _: self.on_create()))
            .pipe(ops.last(), ops.flat_map(lambda _: self.on_submit()))
        )
