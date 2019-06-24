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


"""Read and write DBnomics JSON and TSV files from a Git repository (can be a bare repository).

Using Git vocabulary here:
  - blob: file
  - tree: directory
  - entry: child of tree, (mode, id) tuple
  - object: blob or tree

https://www.dulwich.io/docs/tutorial/file-format.html
"""


import logging
from io import StringIO
from pathlib import Path

from dulwich.objects import Blob

import ujson as json

from . import files
from ..exceptions import StorageError
from .abstract import AbstractDatasetDir, AbstractStorage

git_blob_filemode = 0o100644
git_tree_filemode = 0o040000

log = logging.getLogger(__name__)


class GitStorage(AbstractStorage):
    def __init__(self, repo, provider_code=None, git_ref='HEAD', tree=None, **kwargs):
        self.repo = repo
        self.provider_code = provider_code
        self.git_ref = git_ref
        self._tree = tree
        if provider_code is None:
            provider_json = self.load_provider_json()
            provider_code = provider_json.get("code")
            if provider_code is None:
                raise StorageError("Could not determine provider code")
            self.provider_code = provider_code

    def __repr__(self):
        return "{}({!r}, provider_code={!r}, git_ref={!r}, tree={!r})".format(
            self.__class__.__name__, self.repo, self.provider_code, self.git_ref, self.tree)

    def has_file(self, name):
        return tree_has_blob(self.tree, name)

    def iter_datasets_codes(self):
        for dataset_code, _ in iter_children(self.tree, mode=git_tree_filemode):
            yield dataset_code

    def load_category_tree_json(self):
        return load_json_blob(self.repo, self.tree, "category_tree.json")

    def load_dataset_dir(self, dataset_code):
        return GitDatasetDir(dataset_code, self)

    def load_provider_json(self):
        entry_name = "provider.json"
        provider_json = load_json_blob(self.repo, self.tree, entry_name)
        if provider_json is None:
            raise StorageError("Could not load \"{}\"".format(entry_name), self.provider_code)
        return provider_json

    @property
    def path(self):
        return Path(self.repo.path)

    @property
    def tree(self):
        if self._tree is None:
            self._tree = get_commit_tree(self.repo, self.git_ref, self.path)
            if self._tree is None:
                raise StorageError("Could not load tree", self.provider_code)
        return self._tree


class GitDatasetDir(AbstractDatasetDir):
    def __init__(self, dataset_code, storage, dataset_tree=None):
        self.dataset_code = dataset_code
        self.storage = storage
        self._tree = dataset_tree

    def get_nb_series_from_jsonl(self, series_jsonl_file_name):
        series_jsonl_text = load_text_blob(self.storage.repo, self.tree, series_jsonl_file_name)
        if series_jsonl_text is None:
            raise StorageError("Could not load \"{}\"".format(series_jsonl_file_name),
                               self.storage.provider_code, self.dataset_code)
        with StringIO(series_jsonl_text) as fp:
            nb_series = sum(1 for line in fp if line.strip())
        return nb_series

    def has_any_tsv_file(self):
        for file_name, _ in iter_children(self.tree, mode=git_blob_filemode):
            if file_name.endswith(".tsv"):
                return True
        return False

    def has_file(self, name):
        return tree_has_blob(self.tree, name)

    def iter_observations_from_jsonl(self, series_codes, offset_by_series_code={}):
        raise NotImplementedError(
            "Reading observations from JSON lines file is not supported with GitStorage. Use FileSystemStorage instead.")

    def iter_series_json_from_jsonl(self, series_jsonl_file_name, add_metadata=False):
        series_jsonl_text = load_text_blob(self.storage.repo, self.tree, series_jsonl_file_name)
        if series_jsonl_text is None:
            raise StorageError("Could not load \"{}\"".format(series_jsonl_file_name),
                               self.storage.provider_code, self.dataset_code)
        with StringIO(series_jsonl_text) as fp:
            if add_metadata:
                for line, offset in files.iter_line_offset(fp):
                    series_json = json.loads(line)
                    yield (series_json, {"series_jsonl_offset": offset})
            else:
                for line in fp:
                    series_json = json.loads(line)
                    yield series_json

    def _load_dataset_json(self):
        entry_name = "dataset.json"
        dataset_json = load_json_blob(self.storage.repo, self.tree, entry_name)
        if dataset_json is None:
            raise StorageError("Could not load \"{}\"".format(entry_name),
                               self.storage.provider_code, self.dataset_code)
        return dataset_json

    def load_observations_tsv(self, series_code):
        """Return `str` representing the observations of a time series in TSV."""
        entry_name = "{}.tsv".format(series_code)
        observations_tsv = load_text_blob(self.storage.repo, self.tree, entry_name)
        if observations_tsv is None:
            raise StorageError("Could not load \"{}\"".format(entry_name),
                               self.storage.provider_code, self.dataset_code, series_code)
        return observations_tsv

    @property
    def tree(self):
        if self._tree is None:
            self._tree = load_tree(self.storage.repo, self.storage.tree, self.dataset_code)
            if self._tree is None:
                raise StorageError("Could not load tree", self.storage.provider_code, self.dataset_code)
        return self._tree

# Generic Git read functions


def get_commit_tree(repo, git_ref, path):
    try:
        commit = repo[git_ref.encode('utf-8')]
    except KeyError:
        return None
    commit_tree = commit.tree
    try:
        tree = repo[commit_tree]
    except KeyError:
        return None
    return tree


def iter_children(tree, mode):
    for entry_name in tree:
        entry_type, child_tree_id = tree[entry_name]
        if entry_type == mode:
            entry_name = entry_name.decode('utf-8')
            yield (entry_name, child_tree_id)


def load_json_blob(repo, tree, entry_name):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    blob_str = load_text_blob(repo, tree, entry_name)
    if blob_str is None:
        return None
    try:
        json_blob = json.loads(blob_str)
    except ValueError:
        return None
    return json_blob


def load_text_blob(repo, tree, entry_name, decode=True):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    try:
        entry_mode, entry_id = tree[entry_name]
    except KeyError:
        return None
    if entry_mode != git_blob_filemode:
        return None
    blob_data = repo[entry_id].data
    if not decode:
        return blob_data
    try:
        blob_str = blob_data.decode('utf-8')
    except UnicodeDecodeError:
        return None
    return blob_str


def load_tree(repo, tree, entry_name):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    try:
        entry_mode, entry_id = tree[entry_name]
    except KeyError:
        return None
    if entry_mode != git_tree_filemode:
        return None
    return repo[entry_id]


def tree_has_blob(tree, entry_name):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    try:
        entry_type, _ = tree[entry_name]
    except KeyError:
        return False
    return entry_type == git_blob_filemode


# Generic Git write functions


def add_blob_to_tree(repo, tree, entry_name, text):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    if isinstance(text, str):
        text = text.encode('utf-8')
    assert entry_name, entry_name
    blob = Blob.from_string(text)
    repo.object_store.add_object(blob)
    tree.add(entry_name, git_blob_filemode, blob.id)


def add_tree_to_tree(repo, tree, entry_name, child_tree):
    if isinstance(entry_name, str):
        entry_name = entry_name.encode('utf-8')
    assert entry_name, entry_name
    repo.object_store.add_object(child_tree)
    tree.add(entry_name, git_tree_filemode, child_tree.id)
