from ..config.hashfs import HashFsConfig
from ..primitives.base import maybe_type, flat_to_list
from ..primitives.FS import Directory
from ..primitives.FS import File
from ..exceptions.base import CopyError

import subprocess
from pathlib import Path
from typing import List
import hashlib


class HashFs:
    """
    Content Addressable File System.

    Usage:
    >>> PiClusterHashFs.parse_file(_file=A_LOCAL_FILE, _type=TYPE_TEST, tags=TAGS)

    >>> {'file': piclustert',
         'hash_file_name': 'sha256:6962b617483901846bcb3e5ab052ef6c4efdba6ba3f420e276edf4e020fd28d3',
         'url': '/mnt/clusterfs/hashfs/sha256:6962b617483901846bcb3e5ab052ef6c4efdba6ba3f420e276edf4e020fd28d3'}

    >>> PiClusterHashFs.put(_file=A_LOCAL_FILE, _type=TYPE_TEST, tags=TAGS, commit=False)

    >>> {'file': '/mnt/clusterfs/deployment/picluster/tests/python/picluster/hashfs/test.txt',
         'hash_file_name': 'sha256:6962b617483901846bcb3e5ab052ef6c4efdba6ba3f420e276edf4e020fd28d3',
         'url': '/mnt/clusterfs/hashfs/sha256:6962b617483901846bcb3e5ab052ef6c4efdba6ba3f420e276edf4e020fd28d3',
         'commited': False}
    """

    def __init__(self, root: Directory, algorithm="sha256"):
        self.root = maybe_type(root, Directory)
        self.algorithm = maybe_type(algorithm, str)

    def file_hash(self, url):
        BLOCKSIZE = 65536
        hasher = hashlib.new(self.algorithm)

        with open(maybe_type(url, str), "rb") as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return ":".join([self.algorithm, hasher.hexdigest()])

    def parse_file(self, _file, _type: str, tags: List[str]):
        _hash_file_name = self.file_hash(maybe_type(_file, File).to_path())
        _target_url = "/".join([maybe_type(self.root, str), _hash_file_name])

        return {
            "file": maybe_type(maybe_type(_file, Path).absolute(), str),
            "hash_file_name": _hash_file_name,
            "url": _target_url,
            "tags": tags,
        }

    def _get_target_url(self, _type: str, tags: List[str], file_name: str):
        tags.sort()
        return "/".join(
            [
                str(self.root),
                _type,
                "_".join([t.lower() for t in tags]),
                self.file_hash(file_name),
            ]
        )

    def put(self, _file, _type: str, tags: List[str], commit=False):
        # TODO auto_update: 对之前存在的文件的检查应该在更新数据库时进行
        parsed_file = self.parse_file(_file=_file, _type=_type, tags=tags)
        parsed_file["commited"] = commit

        if commit:
            parsed_file["copy_result"] = try_cp(parsed_file["file"], parsed_file["url"])
            return parsed_file
        else:
            return parsed_file


PiClusterHashFs = HashFs(root=HashFsConfig.Root, algorithm=HashFsConfig.Algorithm)


def try_cp(source, target):
    source_checked = maybe_type(maybe_type(source, File), str)
    target = maybe_type(target, Path)
    if target.is_file():
        return "Target already exists, nothing changed"
    if target.parent.is_dir():
        return shell_run(f"cp {source_checked} {target}")
    else:
        raise CopyError(f"""Target directory: {target.parent} not exist.""")


def shell_run(cmd: str):
    return (
        subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE)
        .stdout.decode()
        .split("\n")[:-1]
    )
