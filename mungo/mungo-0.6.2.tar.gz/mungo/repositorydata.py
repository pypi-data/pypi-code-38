import bz2
import json
import os
import msgpack
from collections import defaultdict
from datetime import datetime, timezone
from os.path import getmtime, basename
from time import time
from typing import DefaultDict, List
from urllib.error import URLError
from urllib.request import Request, urlopen

from tqdm import tqdm

from mungo.common import BFMT, QUIET


def get_repository_data(channels: list,
                        n_jobs: int = 8,
                        offline: bool = False,
                        force_download: bool = False) -> List['RepositoryData']:
    # retrieve repodata asynchronously
    urls = []
    for channel in channels:
        for arch in ['linux-64', 'noarch']:
            if channel != "defaults":
                urls.append((f"https://conda.anaconda.org/{channel}/{arch}", f"{channel}/{arch}"))
            else:
                for c in ['main', 'free', 'pro', 'r']:
                    urls.append((f"https://repo.anaconda.com/pkgs/{c}/{arch}", f"{c}/{arch}"))

    from joblib import Parallel, delayed

    with tqdm(desc="Retrieving repository data", total=len(urls), position=1, bar_format=BFMT, disable=QUIET) as t:
        repos = Parallel(n_jobs=n_jobs, prefer="threads")(
            delayed(download_repo)(url, name, offline, force_download, t) for url, name in urls)
        # tqdm.write(f"Downloading repository data: {time() - t.start_t:.2f}s")
    return repos


def merge_repository_data(repository_data_list: List['RepositoryData']) -> 'RepositoryData':
    # ret = RepositoryData.empty()
    ret = repository_data_list[0]
    # deepcopy since we do not want to modify the contents of `repository_data_list[0].d`!
    # ret.d = copy.deepcopy(repository_data_list[0].d)
    for r in tqdm(repository_data_list[1:], desc="Merging repository data", position=2, bar_format=BFMT, disable=QUIET):
        for name, versions in r.d.items():
            for version in versions:
                if version not in ret.d[name]:
                    ret.d[name][version] = r.d[name][version]
    return ret


def parse_repository_data(repository_name: str, json_data: dict) -> DefaultDict[str, dict]:
    ret = defaultdict(dict)

    if json_data is None:
        return ret

    packages = json_data["packages"]

    for filename, p in packages.items():
        new_build = p["build"].rsplit("_", 1)[0]  # remove _buildnumber from build
        new_version = (p["version"], new_build)
        build_number = p["build_number"]

        p["fn"] = filename

        # different urls for main repositories
        if repository_name.split("/")[0] in ["main", "free", "pro", "r"]:
            p["channel"] = f"https://repo.continuum.io/pkgs/{repository_name}"
        else:
            p["channel"] = f"https://conda.anaconda.org/{repository_name}"

        if new_version not in ret[p["name"]] or ret[p["name"]][new_version]["build_number"] < build_number:
            ret[p["name"]][new_version] = p

    for name, versions in ret.items():
        for v_name, v_value in versions.items():
            v_value["reponame"] = repository_name
    return ret


class RepositoryData:
    def __init__(self, name: str, data: defaultdict):
        self.name = name
        self.d = data

    @classmethod
    def empty(cls) -> 'RepositoryData':
        return cls(None, defaultdict(dict))

    @classmethod
    def _from_json(cls,
                   name: str,
                   json_data: dict) -> 'RepositoryData':
        repository_data = parse_repository_data(name, json_data)
        return cls(name, repository_data)

    @classmethod
    def _from_packed(cls, name: str, file: str, method=msgpack,
                     method_kwargs=dict(use_list=False, raw=False)) -> 'RepositoryData':
        with open(file, 'rt' if method in {json} else 'rb') as reader:
            repository_data = method.load(reader, **method_kwargs)
        return cls(name, repository_data)

    @classmethod
    def _from_file(cls, name: str, filename: str, **kwargs) -> 'RepositoryData':
        opener = bz2.open if filename.endswith('.bz2') else open
        with opener(filename, 'rb') as reader:
            json_data = json.load(reader)
        return cls._from_json(name, json_data, **kwargs)

    @classmethod
    def from_environment(cls, environment: str) -> 'RepositoryData':
        ret = defaultdict(dict)
        # This is a linux only, default path only version of conda's `list_all_known_prefixes`.
        environments_file = os.path.expanduser('~/.conda/environments.txt')
        if not os.path.exists(environments_file):
            raise ValueError("Could not read environment information from ~/.conda/environments.txt.")
        with open(environments_file, 'rt') as reader:
            # FIXME assumption that first line of environments.txt corresponds to base env path might be incorrect
            default_env_path = reader.readline().strip()
            env_map = {basename(path): path for path in map(str.strip, reader)}
            # env_map[default_env_name] = default_env_path
        if environment == "base" or environment == "":
            meta_dir = os.path.join(default_env_path, "conda-meta")
        else:
            env_path = env_map.get(environment)
            if env_path is None:
                raise ValueError(f"No such environment {environment}.")
            meta_dir = os.path.join(env_path, "conda-meta")

        for file in os.listdir(meta_dir):
            if not file.endswith(".json"):
                continue

            with open(os.path.join(meta_dir, file), 'rb') as reader:
                p = json.load(reader)
                name = p["name"]
                p["installed"] = True
            new_version = (p["version"], p["build"])
            ret[name][new_version] = p
        return cls(environment, ret)

    @classmethod
    def from_url(cls,
                 url: str,
                 repository_name: str,
                 offline: bool = False,
                 force_download: bool = False) -> ('RepositoryData', float):
        repodata_url = url + "/repodata.json.bz2"
        local_dir = os.path.expanduser(os.path.join(_cachedir(), 'conda', 'repos', repository_name))
        local_file = os.path.join(local_dir, 'repodata.dump')
        headers = {}

        if offline:  # TODO if offline check if msgpack exist
            return cls._from_packed(repository_name, local_file), None

        if not force_download and os.path.exists(local_file):
            local_timestamp = _mtime(local_file)
            d = local_timestamp.strftime('%a, %d %b %Y %H:%M:%S %Z')
            headers["If-Modified-Since"] = d
        request = Request(repodata_url, headers=headers)
        # The following code is slightly unwieldy, sorry for that
        with urlopen(Request(repodata_url, method='HEAD')) as conn:
            last_modified = conn.headers.get('last-modified', None)
            if last_modified is not None:
                last_modified = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
                last_modified = last_modified.replace(tzinfo=timezone.utc).timestamp()
                if os.path.exists(local_file):
                    if last_modified <= _mtime_timestamp(local_file) and not force_download:
                        return cls._from_packed(repository_name, local_file), last_modified
        try:
            with urlopen(request) as conn:
                json_data_compressed = conn.read()
                data = json.loads(bz2.decompress(json_data_compressed))
                repodata = cls._from_json(repository_name, data)
                return repodata, last_modified
        except URLError as e:
            if e.getcode() == 304:  # NOT MODIFIED
                return cls._from_packed(repository_name, local_file), last_modified
            else:
                raise e


def download_repo(url: str, name: str, offline: bool = False, force_download: bool = False, t: tqdm = None):
    repodata, remote_mtime = RepositoryData.from_url(url, name, offline, force_download)
    if not offline or force_download:
        _store_repodata(repodata, remote_mtime=remote_mtime, force_store=force_download)
    t.update(1)
    return repodata


def _store_repodata(repodata: 'RepositoryData', force_store=False, remote_mtime=None, method=msgpack,
                    method_kwargs={}):
    name = repodata.name
    local_dir = os.path.expanduser(os.path.join(_cachedir(), 'conda', 'repos', name))
    local_file = os.path.join(local_dir, 'repodata.dump')
    if os.path.exists(local_file):
        local_mtime = _mtime_timestamp(local_file)
        if force_store or not remote_mtime or remote_mtime > local_mtime:
            # print(f"Remote {name}/repodata is newer, updating {local_file}.")
            with open(local_file, 'wt' if method in {json} else 'wb') as writer:
                method.dump(repodata.d, writer, **method_kwargs)
            os.utime(local_file, (remote_mtime, remote_mtime))
        else:
            # print(f"{local_file} is up to date")
            pass
    else:
        # print(f"Saving {name}/repodata to {local_file}")
        os.makedirs(local_dir, exist_ok=True)
        with open(local_file, 'wt' if method in {json} else 'wb') as writer:
            method.dump(repodata.d, writer, **method_kwargs)
        if remote_mtime:
            os.utime(local_file, (remote_mtime, remote_mtime))


def _mtime(filename: str) -> datetime:
    return datetime.fromtimestamp(getmtime(filename))


def _mtime_timestamp(filename: str) -> float:
    return _mtime(filename).replace(tzinfo=timezone.utc).timestamp()


def _cachedir() -> str:
    return os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
