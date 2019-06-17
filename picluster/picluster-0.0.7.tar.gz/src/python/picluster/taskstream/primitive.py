import sys
import typing
from typing import Callable, Generic
import attr
import subprocess
from pathlib import Path
from functools import partial, reduce
import rx
from rx import Observable
from rx import operators as ops

from ..interactive.web import Request, _to_graphql_style_array
from ..config.graphql import GraphQLConfig
from ..backend.slurm.slurm import SlurmSjtu
from ..database.model.schema import Task, TaskState


T = typing.TypeVar("T")


def tap(fn):
    def result(x):
        fn(x)
        return x

    return ops.map(result)


def func(fn: Callable) -> Observable:
    """
    Turn a function to Observable.
    """
    return rx.create(fn)


# @attr.s(auto_attribs=True)
# class Resource(Generic[T]):
#     """
#     A resource which is queryable from database
#     """
#
#     id: int


# class Query(Request):
#     """
#     Parse a url to a real resource, e.g. a Path, via query to database
#
#     usage:
#     Query.from_resource(Resource(table_name='ioCollections', primary_key=1)).subscribe(print)
#     """
#
#     def __init__(self, url=None):
#         if url is not None:
#             self.url = url
#         else:
#             self.url = super().url()
#
#     def url(self):
#         return self.url
#
#     @classmethod
#     def from_resource(cls, resource: Resource) -> func:
#         return rx.of(
#             Request.read(
#                 table_name="resources",
#                 select="id",
#                 condition=str(resource.id),
#                 returns=["urls"],
#             )
#         )


def task(t: Task) -> func:
    def _task(observer, scheduler):
        try:
            observer.on_next(t)
            observer.on_completed()
        except Exception as e:
            observer.on_error(e)

    return rx.create(_task)


def is_file(file: "URL") -> bool:
    def _is_file(observer, scheduler):
        try:
            f = Path(file)
            observer.on_next(f.is_file())
            observer.on_completed()
        except Exception as e:
            observer.on_error(f"{f} is not a url.")

    return rx.create(_is_file)


def create(item: T, table_name: str):
    """create a record in database for one item, e.g. a File"""
    if isinstance(item, dict):
        pass
    else:
        try:
            item = attr.asdict(item)
        except Exception as e:
            print(f"Type error, not supported item. {e}")

    result = Request.insert(table_name=table_name, inserts=attr.asdict(item))
    result_id = GraphQLConfig.insert_returning_parser(result)

    pass
    # return Resource(table_name=table_name, primary_key=result_id)


def submit(
    task: Task, backend: "Scheduler" = SlurmSjtu, track_in_db=False
) -> "Observable['output']":
    """
    Submit a **Task** to a scheduler, in the future, we may directly extend rx.Scheduler to fit our use.
    thus, currently, we need use submit(a_task, Slurm('192.168.1.131')).subscribe()
    in the future, we may use a_task.observe_on(Slurm('192.168.1.131')).subscribe() or a_task.subscribe_on(Slurm('ip'))
    """

    def _submit(obs, scheduler):
        id_on_backend = int(backend.submit(task))
        if id_on_backend is not None:
            t = attr.evolve(
                task,
                id_on_backend=id_on_backend,
                state=TaskState.Running,
                state_on_backend=TaskState.Running,
            )
            obs.on_next(t)
            obs.on_completed()
            return
        raise Exception

    def _on_running(task: Task):
        slurm_id = task.id_on_backend
        return SlurmSjtu.completed().pipe(
            ops.filter(lambda completed: slurm_id in completed),
            ops.first(),
            ops.map(lambda _: task),
        )

    def _on_completed(task):
        return attr.evolve(
            task, state=TaskState.Completed, state_on_backend=TaskState.Completed
        )

    def _on_return(task):
        outputs = task.outputs
        work_dir = task.workdir

        def exists(item):
            item_path = Path(str(work_dir) + "/" + str(item))
            if item_path.is_dir() or item_path.is_file():
                return True
            return False

        if len(outputs) > 0:
            if reduce(lambda x, y: x or y, list(map(exists, outputs))):
                return list(map(lambda item: str(work_dir) + "/" + str(item), outputs))
            else:
                raise FileNotFoundError(
                    f"One or more excepted outputs in {outputs} not found."
                )
        return []

    return rx.create(_submit).pipe(
        ops.flat_map(_on_running), ops.map(_on_completed), ops.map(_on_return)
    )


def is_duplicate_task(task: Task):
    def _is_duplicate_task():
        duplicated_task = Request.read_tasks(
            select="inputs", where=_to_graphql_style_array(task.inputs)
        )
        num_duplicated_tasks = len(duplicated_task)

        if num_duplicated_tasks:
            assert num_duplicated_tasks == 1
            duplicated_task_state = duplicated_task[0].state

            if TaskState.Completed is duplicated_task_state:
                print(
                    f"""Task with resources id: {task.inputs} has been executed, will return output of previous task: {duplicated_task[0].id}.""",
                    file=sys.stderr,
                )
                return True
            else:
                return False
        else:
            return False

    return rx.from_callable(_is_duplicate_task)
