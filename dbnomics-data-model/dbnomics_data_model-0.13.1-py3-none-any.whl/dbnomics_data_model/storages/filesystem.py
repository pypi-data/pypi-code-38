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


"""Read and write DBnomics JSON and TSV files from the filesystem."""


import logging
from pathlib import Path

import ujson as json

from . import files
from ..exceptions import StorageError
from .abstract import AbstractDatasetDir, AbstractStorage

log = logging.getLogger(__name__)


class FileSystemStorage(AbstractStorage):
    def __init__(self, storage_dir_path, provider_code=None, **kwargs):
        self.storage_dir_path = Path(storage_dir_path)
        self.provider_code = provider_code
        if provider_code is None:
            provider_json = self.load_provider_json()
            provider_code = provider_json.get("code")
            if provider_code is None:
                raise StorageError("Could not determine provider code")
            self.provider_code = provider_code

    def __repr__(self):
        return "{}({!r}, provider_code={!r})".format(self.__class__.__name__, str(self.storage_dir_path), self.provider_code)

    def has_file(self, name):
        return (self.path / name).is_file()

    def iter_datasets_codes(self):
        for child in self.path.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                yield child.name

    def load_category_tree_json(self):
        return load_json_file(self, self.path / "category_tree.json")

    def load_dataset_dir(self, dataset_code):
        return FileSystemDatasetDir(dataset_code, self)

    def load_provider_json(self):
        filename = "provider.json"
        provider_json = load_json_file(self, self.path / filename)
        if provider_json is None:
            raise StorageError("Could not load \"{}\"".format(filename), self.provider_code)
        return provider_json

    @property
    def path(self):
        return self.storage_dir_path

    def relative_path(self, path):
        return path.relative_to(self.path)


class FileSystemDatasetDir(AbstractDatasetDir):
    def __init__(self, dataset_code, storage):
        self.dataset_code = dataset_code
        self.storage = storage

    def get_nb_series_from_jsonl(self, series_jsonl_file_name):
        with (self.path / series_jsonl_file_name).open() as fd:
            return sum(1 for line in fd if line.strip())

    def has_any_tsv_file(self):
        return any(str(child).endswith(".tsv") for child in self.path.iterdir())

    def has_file(self, name):
        return (self.path / name).is_file()

    def iter_observations_from_jsonl(self, series_codes, offset_by_series_code={}):
        def iter_observations_by_scanning(fp, series_codes: set):
            nb_yielded = 0
            for line in fp:
                if not line:
                    continue
                series_json = json.loads(line)
                series_code = series_json["code"]
                if series_code in series_codes:
                    nb_yielded += 1
                    yield (series_code, series_json["observations"])
                if nb_yielded == len(series_codes):
                    break

        def iter_observations_by_seeking(fp, offset_by_series_code):
            """Yield (exception, series_code, observations)"""
            for series_code, offset in offset_by_series_code.items():
                fp.seek(offset)
                line = next(fp)
                try:
                    series_json = json.loads(line)
                except ValueError as exc:
                    # Hint: Solr index is probably not up-to-date.
                    exc1 = ValueError("Could not decode JSON line for series ID {!r} using offset {}. Reason: {}".format(
                        self.series_id_str(series_code), offset, str(exc)))
                    yield (exc1, series_code, None)
                    continue
                if series_json["code"] != series_code:
                    exc = ValueError("Wrong series code for series ID {!r}: found {!r} using offset {}".format(
                        self.series_id_str(series_code), series_json["code"], offset))
                    yield (exc, series_code, None)
                    continue
                yield (None, series_code, series_json["observations"])

        observations_by_series_code = {}

        series_jsonl_file_path = self.path / self.get_series_jsonl_file_name()
        exc_by_series_code = {}

        if offset_by_series_code:
            with series_jsonl_file_path.open() as fp:
                for exc, series_code, observations in iter_observations_by_seeking(fp, offset_by_series_code):
                    if exc is None:
                        observations_by_series_code[series_code] = observations
                    else:
                        exc_by_series_code[series_code] = exc

        # Remaining series are series that were not indexed in Solr (so no offset known) or that could not be loaded by seeking in JSON-lines.
        remaining_series = set(series_codes) - set(offset_by_series_code.keys()) | set(exc_by_series_code.keys())
        if remaining_series:
            with series_jsonl_file_path.open() as fp:
                observations_by_series_code.update(iter_observations_by_scanning(fp, remaining_series))

        for series_code in series_codes:
            observations = observations_by_series_code.get(series_code)
            if observations is None:
                exc = ValueError(
                    "Could not load series ID {!r} in JSON-Lines data".format(self.series_id_str(series_code)))
                exc.__cause__ = exc_by_series_code.get(series_code)
                yield (exc, series_code, None)
            else:
                yield (None, series_code, observations)

    def iter_series_json_from_jsonl(self, series_jsonl_file_name, add_metadata=False):
        series_jsonl_file_path = self.path / series_jsonl_file_name
        if not series_jsonl_file_path.is_file():
            return
        with (series_jsonl_file_path).open() as fp:
            if add_metadata:
                for line, offset in files.iter_line_offset(fp):
                    series_json = json.loads(line)
                    yield (series_json, {"series_jsonl_offset": offset})
            else:
                for line in fp:
                    series_json = json.loads(line)
                    yield series_json

    def _load_dataset_json(self):
        filename = "dataset.json"
        dataset_json = load_json_file(self.storage, self.path / filename)
        if dataset_json is None:
            raise StorageError("Could not load \"{}\"".format(filename), self.storage.provider_code, self.dataset_code)
        return dataset_json

    def load_observations_tsv(self, series_code):
        filename = "{}.tsv".format(series_code)
        observations_tsv = load_text_file(self.storage, self.path / filename)
        if observations_tsv is None:
            raise StorageError("Could not load \"{}\"".format(filename),
                               self.storage.provider_code, self.dataset_code, series_code)
        return observations_tsv


def load_json_file(storage, path):
    try:
        with path.open() as fd:
            try:
                return json.load(fd)
            except ValueError:
                return None
    except FileNotFoundError:
        return None


def load_text_file(storage, path):
    try:
        return path.read_text()
    except FileNotFoundError:
        return None


def remove_first_column(line):
    return "\t".join(line.split("\t")[1:])
