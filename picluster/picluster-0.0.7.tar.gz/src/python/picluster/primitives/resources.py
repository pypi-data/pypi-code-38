from .base import maybe_type
from .FS import Url, File, Directory
from ..database.model.resources import recur_file
from ..interactive.web import Request
from .base import flat_to_list
from ..exceptions.base import DirectoryNotEmptyError
from pathlib import Path
from typing import List


class Resource:
    """
    Abstraction of resources that a task will need on runtime, including resourceFiles, workdir and computation resource.

    Accepts str, Url, File, or Directory.
    """

    @property
    def content(self):
        pass


class FileResource(Resource):
    """
    Accept all kinds of resource, e.g. File, Directory, str[url], int[resource_id], as input and return a list of urls.

    Usage:
    >>> f1 = FileResource(1,2,3,A_DIR,A_FILE)
    >>>
    >>> f1.content
    >>> [PosixPath('/mnt/gluster/resources/phantomHeaders/zql_16Module_1_layers/header_phantomD.h33'),
    >>> PosixPath('/mnt/gluster/resources/phantomHeaders/mct_derenzo_10_layers/header_phantomD.h33'),
    >>> PosixPath('/mnt/gluster/resources/phantomHeaders/mct_jaszczak_10_layers/header_phantomD.h33'),
    >>> PosixPath('/mnt/gluster/resources/phantom/derenzo/derenzo.1/range_material_phantomD.dat'),
    >>> PosixPath('/mnt/gluster/resources/phantom/derenzo/derenzo.1/activity_range_phantomD.dat'),
    >>> PosixPath('/mnt/gluster/resources/phantom/derenzo/derenzo.1/phantomD.bin'),
    >>> PosixPath('/mnt/gluster/resources/phantom/derenzo/derenzo.1/phantomD.bin')]
    """

    def __init__(self, *resources):
        self.trackable = True

        urls = []

        def _take_single_resource(resource):
            resource_id = maybe_type(resource, int)
            if resource_id is None:
                r = None
            else:
                r = Request.by_resource_id(resource_id)
            if r is None:
                r = maybe_type(resource, File)
                self.trackable = False
            if r is None:
                r = maybe_type(resource, Directory)
            if r is None:
                raise TypeError(
                    f"""FileResource got illegal input: {resource}. Accepts directory, file, or resource id."""
                )
            return r

        for resource in resources:
            urls.append(_take_single_resource(resource))
            self.urls = flat_to_list(urls)

    @property
    def content(self):
        def _on_single_content(url):
            if isinstance(url, str):
                return Path(url)
            elif isinstance(url, File):
                return url.to_path()
            elif isinstance(url, Directory):
                return recur_file(url.to_path())

        return flat_to_list(list(map(_on_single_content, self.urls)))


class StorageResource(Resource):
    """
    Handle storage resource requesting, accept only empty directories.
    """

    def __init__(self, work_directory):
        if isinstance(work_directory, Directory):
            self.work_directory = work_directory.to_path()
        else:
            self.work_directory = maybe_type(work_directory, Directory).to_path()

        if self.work_directory is None:
            raise TypeError(
                f"""Except Directory-like object(e.g. str, Url, Directory), got {work_directory}"""
            )

        if not is_empty_path(self.work_directory):
            raise DirectoryNotEmptyError

    @property
    def content(self):
        return self.work_directory


def push_resource(resource: FileResource, resource_type: str, tags: List[str]):
    pass


def is_empty_path(path):
    if not len(list(path.iterdir())):
        return True
    else:
        return False
