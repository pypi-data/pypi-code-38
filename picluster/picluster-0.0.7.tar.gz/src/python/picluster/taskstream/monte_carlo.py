import re
from pathlib import Path
from .cli_tasks import mkdir, mv, cp, mkdir_n_return
from .primitive import Resource, Query, submit, cli, is_duplicate_task
from typing import List
from .combinator import parallel, sequential, parallel_with_error_detect
from ..backend.slurm.slurm import SlurmSjtu
from rx import operators as ops
from functools import partial
import attr
import rx
from ..database.model.schema import Task, TaskState
from ..interactive.web import Request
from datetime import datetime


class MonteCarloSimulation:
    def __init__(
        self,
        work_directory: "Path|str",
        required_resources: 'List[Resource["File"]]',
        nb_subtasks: int,
        scheduler="slurm",
        backend=SlurmSjtu,
        fn="monteCarlo_simu_on_Gate@7.2",
        sub_task_outputs=["result.root"],
        merger_task_output="result.root",
        sub_task_script="run.sh",
    ):
        self.work_directory = Path(work_directory)
        self.required_files = required_resources
        self.nb_subtasks = nb_subtasks
        self.sub_task_script = sub_task_script
        self.fn = fn
        self.sub_task_outputs = sub_task_outputs
        self.merger_task_output = merger_task_output
        self.scheduler = scheduler
        self.backend = backend
        self.Task = Task(
            inputs=sorted([str(i.id) for i in self.required_files]),
            state=TaskState.Created.name,
            scheduler="picluster",
            backend="SlurmSjtu",
            fn=self.fn,
            workdir=self.work_directory,
            outputs=[str(self.work_directory / self.merger_task_output)],
            state_on_backend=None,
        )
        self.observable = self._main()

    def _sub_tasks(self):
        return sequential(
            [
                mkdir_n_return(self.work_directory),
                parallel_with_error_detect(
                    [self._sub_task(d) for d in self._sub_dirs()]
                ),
            ]
        )

    def _sub_dirs(self):
        return make_sub_directories(
            root=self.work_directory, nb_sub_directories=self.nb_subtasks
        )

    def _sub_task(self, sub_dir):
        return sequential(
            [mkdir_n_return(sub_dir), self.load_required_files_to_directory]
        ).pipe(ops.last(), ops.flat_map(lambda _: self._submit_sub_task(sub_dir)))

    def _merger_task(self, sub_outputs):
        def _submit_merge_task():
            task = Task(
                workdir=self.work_directory,
                fn=self.fn,
                outputs=self.merger_task_output,
                scheduler=self.scheduler,
            )
            return hadd(
                hadd_output=str(task.workdir) + "/" + str(task.outputs),
                sub_outputs=sub_outputs,
            )

        return _submit_merge_task()

    def _submit_sub_task(self, work_dir: str):
        def _sub_task():
            return Task(
                workdir=work_dir,
                script=self.sub_task_script,
                fn=self.fn,
                outputs=self.sub_task_outputs,
                scheduler=self.scheduler,
            )

        task = _sub_task()
        return submit(task=task, backend=self.backend)

    def _parse_merger_output(self, merger_output):
        if "hadd Target file: " in merger_output[0]:
            result_url = re.sub(r"hadd Target file: ", "", merger_output[0])
            # TODO need either url/path
            if str(result_url) == str(self.work_directory / self.merger_task_output):
                return result_url

    def load_required_files_to_directory(self, directory: Path):
        if not isinstance(directory, Path):
            # print(f"DEBUG: load_required_files_to_directory {directory}")
            directory = Path(directory)

        def _load_one_required_resource(resource):
            resource_urls = Query.from_resource(resource).pipe(
                ops.reduce(lambda x, y: x + y)
            )
            return resource_urls.pipe(
                ops.flat_map(rx.from_),
                ops.flat_map(
                    lambda resource_url: cp(source=resource_url, target=directory)
                ),
            )

        return parallel(
            tasks=[
                _load_one_required_resource(resource)
                for resource in self.required_files
            ]
        )

    def _is_backend_avaliable(self):
        def _is_not_overload(x):
            return x is False

        return self.backend.is_overload().pipe(
            ops.filter(_is_not_overload), ops.take(1), ops.map(lambda _: True)
        )

    def _on_created(self):
        def _create():
            t = attr.evolve(
                self.Task, state=TaskState.Created.name, create=datetime.utcnow()
            )
            # print(f"MC _on_created, creat task: {t}")
            task_id = Request.insert_task(t)
            # print(f"MC _on_created, task_id {task_id}")
            self.Task = attr.evolve(t, id=task_id)
            if isinstance(task_id, int):
                return True
            else:
                raise ValueError(
                    f"Create task error. Expect a int task_id, got: {task_id}, type: {type(task_id)}"
                )

        return rx.from_callable(_create)

    def _on_running(self):
        def _running():
            t = attr.evolve(
                self.Task, state=TaskState.Running.name, submit=datetime.utcnow()
            )
            response = Request.update_task(t)
            # print(f"MC _on_running, task_id {response}")
            return True

        return rx.from_callable(_running)

    def _on_completed(self):
        def _completed():
            t = attr.evolve(
                self.Task, state=TaskState.Completed.name, finish=datetime.utcnow()
            )
            Request.update_task(t)
            return self.Task.outputs

        return rx.from_callable(_completed)

    def _on_duplicate(self):
        def _duplicate():
            return self.Task.outputs

        return rx.from_callable(_duplicate)

    def _main(self):
        complete_mc_task = self._sub_tasks().pipe(
            ops.flat_map(self._merger_task), ops.map(self._parse_merger_output)
        )

        is_dup = is_duplicate_task(self.Task)

        on_duplicated_task = sequential(
            [is_dup.pipe(ops.filter(lambda value: value == True)), self._on_duplicate()]
        )

        on_new_task = sequential(
            [
                is_dup.pipe(ops.filter(lambda value: value == False)),
                self._on_created(),
                self._is_backend_avaliable(),
                self._on_running(),
                lambda _: complete_mc_task,
                self._on_completed(),
            ]
        )

        return parallel([on_duplicated_task, on_new_task])


def debug_print(text):
    return cli(f"echo {text}")


def make_sub_directories(
    root: Path, nb_sub_directories: int, prefix="sub"
) -> "List[str]":
    if not isinstance(root, Path):
        root = Path(root)
    return [root / f"{prefix}.{i}" for i in range(nb_sub_directories)]


def hadd(sub_outputs: list, hadd_output: str):
    def to_string(l):
        return " ".join(l)

    return cli(f"hadd {hadd_output} {to_string(sub_outputs)}")
