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

import abc
import logging
from io import StringIO

from toolz import count, pipe

from .. import datasets
from ..exceptions import StorageError
from ..observations import iter_tsv_decoded_rows, iter_tsv_rows

log = logging.getLogger(__name__)

DEFAULT_SERIES_JSONL_FILE_NAME = "series.jsonl"


class AbstractStorage(abc.ABC):
    provider_code = None

    def get_nb_datasets(self):
        """Return the number of datasets of a provider.

        This method is intended to be cheap.

        See also: `iter_datasets_codes` and `iter_datasets_dirs`.
        """
        return count(self.iter_datasets_codes())

    @abc.abstractmethod
    def has_file(self, name):
        pass

    @abc.abstractmethod
    def iter_datasets_codes(self):
        """Yield codes as `str` of the datasets of the provider.

        This method is intended to be cheap.

        See also: `self.iter_datasets_dirs`.
        """
        pass

    def iter_datasets_dirs(self, sort_by_dir_name=False):
        """Yield datasets directories as sub-classes of `AbstractDatasetDir`, for the datasets of the provider.

        See also: `self.iter_datasets_codes`, lighter than this one.
        """
        iterator = self.iter_datasets_codes()
        if sort_by_dir_name:
            iterator = sorted(iterator)
        for dataset_code in iterator:
            yield self.load_dataset_dir(dataset_code)

    @abc.abstractmethod
    def load_category_tree_json(self):
        """Return `category_tree.json` content. Since the file is optional, return `None` if not found."""
        pass

    @abc.abstractmethod
    def load_dataset_dir(self, dataset_code):
        pass

    @abc.abstractmethod
    def load_provider_json(self):
        pass

    @property
    @abc.abstractmethod
    def path(self):
        pass


class AbstractDatasetDir(abc.ABC):
    dataset_code = None
    storage = None
    _series_jsonl_file_name = 'unknown'

    def get_nb_series(self, dataset_series="unknown"):
        """Return the number of series of a dataset.

        This method is intended to be cheap.

        See also: `iter_series_json`.
        """
        if isinstance(dataset_series, list):
            return len(dataset_series)
        else:
            series_jsonl_file_name = self.get_series_jsonl_file_name(dataset_series=dataset_series)
            return self.get_nb_series_from_jsonl(series_jsonl_file_name)

    @abc.abstractmethod
    def get_nb_series_from_jsonl(self, series_jsonl_file_name):
        pass

    def get_series_jsonl_file_name(self, dataset_series="unknown"):
        if self._series_jsonl_file_name == "unknown":
            if dataset_series == "unknown":
                dataset_json = self.load_dataset_json()
                dataset_series = dataset_json.get("series")

            series_file_name = None
            if dataset_series is None:
                series_file_name = DEFAULT_SERIES_JSONL_FILE_NAME
            elif isinstance(dataset_series, dict):
                dataset_series_path = dataset_series.get("path")
                if dataset_series_path is not None:
                    series_file_name = dataset_series_path

            self._series_jsonl_file_name = series_file_name

        return self._series_jsonl_file_name

    @abc.abstractmethod
    def has_any_tsv_file(self):
        pass

    @abc.abstractmethod
    def has_file(self, name):
        pass

    def iter_observations(self, series_codes, offset_by_series_code={}):
        """Yield tuples like `(exception, series_code, observations)` corresponding to the given `series_codes`,
        either from `series.jsonl` file, or else from `{series_code}.tsv` files.

        `series_codes` must belong to this dataset.

        Note: `offset_by_series_code` is forwarded to `self.iter_observations_from_jsonl` implementation.
        """
        if self.has_any_tsv_file():
            yield from self.iter_observations_from_tsv(series_codes)
        else:
            yield from self.iter_observations_from_jsonl(series_codes, offset_by_series_code)

    @abc.abstractmethod
    def iter_observations_from_jsonl(self, series_codes, offset_by_series_code={}):
        """Yield tuples like `(exception, series_code, observations)` corresponding to the given `series_codes`,
        from `series.jsonl` file, in that order.

        `series_codes` must belong to this dataset.

        Skip series that could not be found, so this function could yield less items than `len(series_codes)`.

        If the current series code is found in `offset_by_series_code`, `seek` to the given offsets directly.
        Otherwise scan `series.jsonl` to find it (scan is performed once, keeping results in memory).

        Examples:
        self.iter_observations_from_jsonl(["A", "B"])
        self.iter_observations_from_jsonl(["A", "B"], offset_by_series_code={"A": 0, "B": 23})
        """
        pass

    def iter_observations_from_tsv(self, series_codes):
        """Yield tuples like `(exception, series_code, observations)` corresponding to the given `series_codes`,
        from `{series_code}.tsv` files.

        `series_codes` must belong to this dataset.
        """
        for series_code in series_codes:
            try:
                observations_tsv = self.load_observations_tsv(series_code)
            except StorageError as exc:
                yield (exc, series_code, None)
                continue
            with StringIO(observations_tsv) as fp:
                observations = pipe(fp, iter_tsv_rows, iter_tsv_decoded_rows, list)
                yield (None, series_code, observations)

    def iter_series_json(self, add_metadata=False, dataset_series="unknown"):
        """Yield series JSON `dict`s describing time series metadata.

        Series can be:
        - in `dataset.json` under the `series` property (`list`): pass the list to the `dataset_series` argument
        - in a separate `series.jsonl` file (JSON lines format)

        Parameter `add_metadata` is passed to `self.iter_series_json_from_jsonl`.
        If it is `True`, yield tuples like `(series_json, metadata)`.

        See also: `get_nb_series`, lighter than this function because it does not decode JSON documents.
        """
        if isinstance(dataset_series, list):
            if add_metadata:
                for series_json in dataset_series:
                    yield (series_json, {})
            else:
                yield from iter(dataset_series)
        else:
            series_jsonl_file_name = self.get_series_jsonl_file_name(dataset_series=dataset_series)
            yield from self.iter_series_json_from_jsonl(series_jsonl_file_name, add_metadata=add_metadata)

    @abc.abstractmethod
    def iter_series_json_from_jsonl(self, series_jsonl_file_name, add_metadata=False):
        """Yield series JSON `dict`s from `series.jsonl` JSON-lines file.

        If `add_metadata` is `True`, yield tuples like `(series_json, metadata)` where `metadata` is a `dict`
        which content is determined by the `FileSystemDatasetDir` or `GitDatasetDir` implementation.
        """
        pass

    @abc.abstractmethod
    def _load_dataset_json(self):
        pass

    def load_dataset_json(self):
        dataset_json = self._load_dataset_json()
        # Take advantage of having dataset.json content to store series.jsonl file name.
        dataset_series = dataset_json.get("series")
        _ = self.get_series_jsonl_file_name(dataset_series)

        # Set default values in case stored JSON file does not mention them explicitly.
        dimensions_codes_order = dataset_json.get("dimensions_codes_order")
        if dimensions_codes_order is None:
            dataset_json["dimensions_codes_order"] = datasets.get_dimensions_codes_order(dataset_json)

        return dataset_json

    @abc.abstractmethod
    def load_observations_tsv(self, series_code):
        """Return `str` representing the observations of a time series in TSV."""
        pass

    @property
    def path(self):
        return self.storage.path / self.dataset_code

    def series_id(self, series_code):
        return (self.storage.provider_code, self.dataset_code, series_code)

    def series_id_str(self, series_code):
        return "/".join(self.series_id(series_code))
