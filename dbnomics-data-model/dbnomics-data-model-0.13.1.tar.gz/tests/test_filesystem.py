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


from pathlib import Path

from dbnomics_data_model.storages.filesystem import FileSystemStorage

script_dir = Path(__file__).resolve().parent


def test_init():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    assert storage.provider_code == "provider1"


def test_load_provider_json():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    provider_json = storage.load_provider_json()
    assert provider_json["code"] == "provider1"


def test_load_category_tree_json():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    category_tree_json = storage.load_category_tree_json()
    assert category_tree_json[0]["code"] == "c1"


def test_load_dataset_dir():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    dataset_dir = storage.load_dataset_dir("dataset1")
    assert dataset_dir.dataset_code == "dataset1"


def test_iter_datasets_codes():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    datasets_codes = sorted(storage.iter_datasets_codes())
    assert datasets_codes == ["dataset1", "dataset2", "dataset3", "dataset4"]


def test_load_dataset_json():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")
    dataset_dir = storage.load_dataset_dir("dataset1")
    assert dataset_dir._series_jsonl_file_name == "unknown"
    dataset_json = dataset_dir.load_dataset_json()
    assert dataset_json["code"] == "dataset1"
    assert dataset_dir._series_jsonl_file_name == None


def test_get_series_jsonl_file_name():
    storage = FileSystemStorage(script_dir / "fixtures" / "provider1-json-data")

    dataset_dir = storage.load_dataset_dir("dataset1")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name()
    assert series_jsonl_file_name is None

    dataset_dir = storage.load_dataset_dir("dataset1")
    dataset_json = dataset_dir.load_dataset_json()
    dataset_series = dataset_json.get("series")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name(dataset_series=dataset_series)
    assert series_jsonl_file_name is None

    storage = FileSystemStorage(script_dir / "fixtures" / "provider2-json-data")

    dataset_dir = storage.load_dataset_dir("dataset1")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name()
    assert series_jsonl_file_name == "series.jsonl"

    dataset_dir = storage.load_dataset_dir("dataset1")
    dataset_json = dataset_dir.load_dataset_json()
    dataset_series = dataset_json.get("series")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name(dataset_series=dataset_series)
    assert series_jsonl_file_name == "series.jsonl"

    dataset_dir = storage.load_dataset_dir("dataset2")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name()
    assert series_jsonl_file_name == "series.jsonl"

    dataset_dir = storage.load_dataset_dir("dataset2")
    dataset_json = dataset_dir.load_dataset_json()
    dataset_series = dataset_json.get("series")
    series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name(dataset_series=dataset_series)
    assert series_jsonl_file_name == "series.jsonl"
