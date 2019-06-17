from pathlib import Path
from functools import reduce
from operator import and_
import hashlib
from ...interactive.web import Request


def recur_dir(root: "str or Path") -> "List[Dir]":
    result = []

    def _no_sub_dir(root):
        return reduce(and_, [i.is_file() for i in root.iterdir()])

    def _recur_dir(root):
        if not isinstance(root, Path):
            root = Path(root)

        for sub in root.iterdir():
            if sub.is_dir() and _no_sub_dir(sub):
                result.append(sub)
            else:
                _recur_dir(sub)

    _recur_dir(root)
    return result


def recur_file(root: "str or Path") -> "List[File]":
    result = []

    def _recur_file(root):
        if not isinstance(root, Path):
            root = Path(root)

        for sub in root.iterdir():
            if sub.is_file():
                result.append(sub)
            elif sub.is_dir():
                _recur_file(sub)

    _recur_file(root)
    return result


def parse_resource(directory: Path, root="/mnt/gluster/resources"):
    directory = Path(directory)

    def _parse_dir(directory: Path):
        files = list(directory.iterdir())

        try:
            directory = directory.relative_to(root)
        except Exception as e:
            print(f"{e}: Only accept resources under directory: {root}")

        directory_in_list = str(directory).split("/")

        return {
            "type": directory_in_list[0],
            "comments": "_".join(directory_in_list[1:]),
            "hash": _resource_hash(files),
            "urls": _urls_to_string(files),
        }

    def _resource_hash(files: "List[Path]"):
        def _hash(url):
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()

            with open(url, "rb") as afile:
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            return hasher.hexdigest()

        files_hash = list(map(_hash, files))
        files_hash.sort()
        return "".join(files_hash)

    def _urls_to_string(urls):
        if isinstance(urls, str):
            return "{" + str(urls) + "}"
        elif isinstance(urls, list):
            return "{" + ", ".join([str(f) for f in urls]) + "}"

    return _parse_dir(directory)


def sync_resource(resource_dict):
    duplicated_item_id = Request.read(
        table_name="resources",
        select="hash",
        condition=resource_dict["hash"],
        returns=["id"],
    )

    modified_item_id = Request.read(
        table_name="resources",
        select="urls",
        condition=resource_dict["urls"],
        returns=["id"],
    )

    if len(duplicated_item_id):
        raise ValueError(f"Duplicated item with resource id: {duplicated_item_id}.")

    if len(modified_item_id):
        for i in modified_item_id:
            if i in modified_item_id and i not in duplicated_item_id:
                Request.updates(table_name="resources", id=i, patches=resource_dict)
                raise ValueError(
                    f"Modified item with resource id: {modified_item_id}, already updated."
                )

    return Request.insert(table_name="resources", inserts=resource_dict)


def sync_resources(work_dir):
    # TODO: error info for illegal resource dir not coherent
    resources = recur_dir(work_dir)

    for r in resources:
        try:
            result = sync_resource(parse_resource(r))
            print(result)
        except Exception as e:
            print(e)
            pass
