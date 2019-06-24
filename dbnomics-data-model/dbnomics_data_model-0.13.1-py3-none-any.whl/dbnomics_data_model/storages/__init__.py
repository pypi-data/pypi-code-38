# dbnomics-data-model -- Define, validate and transform DBnomics data.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2017-2018 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-data-model
#
# dbnomics-data-model is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-data-model is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Storages initialization functions"""


import logging
from pathlib import Path

from dulwich.errors import NotGitRepository
from dulwich.repo import Repo

from . import git
from .. import series
from ..exceptions import StorageError
from .filesystem import FileSystemStorage
from .git import GitStorage

log = logging.getLogger(__name__)


def get_storage_dir_path(json_data_base_dir_path, provider_code):
    json_data_base_dir_path = Path(json_data_base_dir_path)
    provider_lowercase = provider_code.lower()
    storage_dir_name = "{}-json-data.git".format(provider_lowercase)
    storage_dir_path = json_data_base_dir_path / storage_dir_name
    if not storage_dir_path.is_dir():
        # Try without `.git` suffix.
        storage_dir_name = "{}-json-data".format(provider_lowercase)
        storage_dir_path = json_data_base_dir_path / storage_dir_name
        if not storage_dir_path.is_dir():
            return None
    return storage_dir_path


def init_storage(storage_dir_path, provider_code=None, **kwargs):
    """Return a `FileSystemStorage` instance if regular files are checkouted,
    otherwise return a `GitStorage` instance.

    Prefer `FileSystemStorage` over `GitStorage` because regular files can be read in stream mode,
    whereas Git blobs must be loaded completely in RAM.
    """
    storage_dir_path = Path(storage_dir_path)
    if not storage_dir_path.is_dir():
        raise StorageError("Could not find storage directory", provider_code)
    try:
        repo = Repo(str(storage_dir_path))
    except NotGitRepository:
        repo = None
    if repo is not None and repo.bare:
        log.debug("Opening {!r} as a Git storage".format(str(storage_dir_path)))
        return GitStorage(repo, provider_code, **kwargs)
    else:
        log.debug("Opening {!r} as a file-system storage".format(str(storage_dir_path)))
        return FileSystemStorage(storage_dir_path, provider_code, **kwargs)


def iter_storages(json_data_base_dir_path, series_ids, **kwargs):
    """Yield `(storage, series_codes_by_dataset_code)`, where series of `series_codes_by_dataset_code`
    belong to the provider opened by `storage`.

    The `series_ids` parameter can contain series IDs from different providers and datasets.
    """
    series_ids_tree = series.series_ids_to_tree(series_ids)
    for provider_code, series_codes_by_dataset_code in series_ids_tree.items():
        storage_dir_path = get_storage_dir_path(json_data_base_dir_path, provider_code)

        if storage_dir_path is None:
            error = StorageError("Could not find storage directory", provider_code)
            yield (None, None, error)
            continue

        try:
            storage = init_storage(storage_dir_path, provider_code, **kwargs)
        except StorageError as error:
            yield (None, None, error)
            continue

        yield (storage, series_codes_by_dataset_code, None)
