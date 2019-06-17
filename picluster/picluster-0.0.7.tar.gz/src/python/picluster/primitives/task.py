import abc
from abc import ABC
import rx
import attr
import hashlib
from pathlib import Path

# from ..backend.slurm.slurm import SlurmSjtu
from datetime import datetime
from .base import maybe_type
from ..interactive.web import Request
from ..database.model.schema import Task, TaskState
from .resources import FileResource, StorageResource
from ..taskstream.cli_tasks import CLI
from ..taskstream.combinator import parallel


class TASK(ABC):
    def __init__(
        self,
        file_resources: FileResource,
        storage_resource: StorageResource,
        backend,
        tags,
        fn,
        output,
        commit=False,
        clean_work_dir_after_complete=False,
    ):
        self.file_resources = file_resources
        self.storage_resource = storage_resource
        self.work_dir = self.storage_resource.content
        self.backend = backend
        self.output = output
        self.commit = commit
        self.clean_work_dir_after_complete = clean_work_dir_after_complete
        self.tags = tags
        self.output = [self.work_dir / output]
        self.Task = Task(
            fn=fn,
            outputs=self.output,
            state=TaskState.Created.name,
            workdir=self.work_dir,
        )
        pass

    @abc.abstractmethod
    def on_create(self):
        return rx.from_callable(_create(self.Task))

    @abc.abstractmethod
    def on_submit(self):
        pass

    @abc.abstractmethod
    def on_error(self):
        pass

    @abc.abstractmethod
    def on_complete(self):
        pass

    @abc.abstractmethod
    def observable(self):

        pass


class TaskUtils:
    # @staticmethod
    # def _create(task):
    #     t = attr.evolve(task, state=TaskState.Created.name, create=datetime.utcnow())
    #     task_id = Request.insert_task(t)
    #     task = attr.evolve(t, id=maybe_type(task_id))
    #     return task

    # @staticmethod
    # def load_resources_to_work_directory(
    #     source: FileResource, work_dir: StorageResource
    # ):
    #     buf = []
    #     for i in source.content:
    #         CLI.cp(source=i, target=work_dir.content)
    #     return parallel(buf)

    @staticmethod
    def file_hash(url):
        BLOCKSIZE = 65536
        hash_algorithm = "sha256"
        hasher = hashlib.new(hash_algorithm)

        with open(maybe_type(url, str), "rb") as file:
            buf = file.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = file.read(BLOCKSIZE)
        return ":".join([hash_algorithm, hasher.hexdigest()])

    @staticmethod
    def string_hash(str_):
        hash_object = hashlib.sha256(str_.encode(encoding="UTF-8", errors="strict"))
        return "sha256:" + hash_object.hexdigest()
