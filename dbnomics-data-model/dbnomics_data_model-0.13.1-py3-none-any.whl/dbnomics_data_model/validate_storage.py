#! /usr/bin/env python3

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


"""Validate a DBnomics storage directory containing data from a provider."""

import argparse
import io
import logging
import sys
from collections import defaultdict
from pathlib import Path

import jsonschema.exceptions
from toolz import get, take

import ujson as json
from dbnomics_data_model import storages, validators
from dbnomics_data_model.exceptions import StorageError
from dbnomics_data_model.observations import (NOT_AVAILABLE,
                                              detect_period_format_strict,
                                              value_to_float)

log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('storage_dir', type=Path, help='path of directory '
                        'containing DBnomics series from a provider (in JSON and TSV formats)')
    parser.add_argument('--bare-repo-fallback', action='store_true',
                        help="if storage_dir does not exist, try with <storage_dir>.git")
    parser.add_argument('--format', choices=["jsonl", "text"], default="text", help="format of the error report")
    parser.add_argument('--ignore-errors', help='codes of errors to ignore, comma-separated if multiple'
                        ' (example: --ignore-errors invalid-provider-directory-name)')
    parser.add_argument('--log', default='WARNING', help='level of logging messages')
    parser.add_argument('--only-datasets', help='codes of datasets to validate, comma-separated')
    parser.add_argument('--all-series', action='store_true', help='validate all series')
    parser.add_argument('--max-series', type=int, default=100, help='Max number of series to validate per dataset')
    parser.add_argument('--all-observations', action='store_true', help='validate all observations')
    parser.add_argument('--max-observations', type=int, default=100,
                        help='Max number of observations to validate per series')
    args = parser.parse_args()

    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(args.log))
    logging.basicConfig(
        format="%(levelname)s:%(name)s:%(message)s",
        level=numeric_level,
        stream=sys.stderr,
    )

    args.ignore_errors = args.ignore_errors.strip().split(",") \
        if args.ignore_errors is not None \
        else []
    args.only_datasets = args.only_datasets.strip().split(",") \
        if args.only_datasets is not None \
        else []
    if args.all_series:
        args.max_series = None
    if args.all_observations:
        args.max_observations = None

    try:
        args.storage_dir = args.storage_dir.resolve()
    except FileNotFoundError:
        if not args.bare_repo_fallback:
            raise
        bare_storage_dir = args.storage_dir.with_suffix(".git")
        if not args.storage_dir.is_dir() and bare_storage_dir.is_dir():
            log.info("Storage directory %r does not exist but --bare-repo-fallback option was used, and bare storage directory %r exists, so using it",
                     str(args.storage_dir), str(bare_storage_dir))
            args.storage_dir = bare_storage_dir

    log.debug("Loading storage...")
    try:
        storage = storages.init_storage(args.storage_dir)
    except StorageError as exc:
        print(format_error({
            **error_from_storage_error(exc),
            "location": ".",
        }, output_format=args.format))
        return -1

    errors_codes = defaultdict(int)

    try:
        log.debug("Validating provider...")
        _, provider_errors = validate_provider(storage, ignore_errors=args.ignore_errors,
                                               storage_dir_name=args.storage_dir.name)
        for error in provider_errors:
            errors_codes[error['error_code']] += 1
            print(format_error(error, output_format=args.format))

        log.debug("Validating category tree...")
        category_tree_errors = validate_category_tree(storage, ignore_errors=args.ignore_errors)
        for error in category_tree_errors:
            errors_codes[error['error_code']] += 1
            print(format_error(error, output_format=args.format))

        log.debug("Validating datasets...")
        nb_datasets = storage.get_nb_datasets()
        for dataset_index, dataset_dir in enumerate(storage.iter_datasets_dirs(sort_by_dir_name=True), start=1):
            dataset_code = dataset_dir.dataset_code
            if args.only_datasets and dataset_code not in args.only_datasets:
                continue

            log.debug("Validating dataset %s (%d/%d) (except its series)...", dataset_code, dataset_index, nb_datasets)
            _, dataset_series, dataset_errors = validate_dataset(dataset_dir, ignore_errors=args.ignore_errors)
            for error in dataset_errors:
                errors_codes[error['error_code']] += 1
                print(format_error(error, output_format=args.format))

            log.debug("Validating series of dataset %r...", dataset_code)
            series_errors = validate_series(dataset_dir, dataset_series, ignore_errors=args.ignore_errors,
                                            max_series=args.max_series, max_observations=args.max_observations)
            for error in series_errors:
                errors_codes[error['error_code']] += 1
                print(format_error(error, output_format=args.format))

    except KeyboardInterrupt as e:
        logging.exception(e)
    finally:
        if args.max_series is not None:
            print("\nNote: not all series of each datasets have been checked (maximum {} per dataset actually).\nTo check all series of all datasets, use \"--all-series\" option".format(args.max_series))
        if args.format == "text" and errors_codes:
            print("\nEncountered errors codes:\n{}".format(
                "\n".join(list("    - {}: {}".format(k, v) for k, v in errors_codes.items()))))

    return len(errors_codes)


def error_from_storage_error(exc: StorageError):
    return {
        "error_code": "storage-error",
        "message": exc.base_message,
        "provider_code": exc.provider_code,
        "dataset_code": exc.dataset_code,
        "series_code": exc.series_code,
    }


def format_error(error, output_format="text"):
    if output_format == "jsonl":
        return json.dumps(error, sort_keys=True)

    sio = io.StringIO()

    sio.write("- ")

    provider_code = error.get("provider_code")
    dataset_code = error.get("dataset_code")
    series_code = error.get("series_code")
    if provider_code is not None and dataset_code is not None and series_code is not None:
        sio.write('Series "{}/{}/{}" '.format(provider_code, dataset_code, series_code))
    elif provider_code is not None and dataset_code is not None:
        sio.write('Dataset "{}/{}" '.format(provider_code, dataset_code))
    elif provider_code is not None:
        sio.write('Provider "{}" '.format(provider_code))

    location = error.get("location")
    if location is not None:
        sio.write("at location {} ".format(location))

    line_number = error.get("line_number")
    if line_number is not None:
        sio.write("(line {}) ".format(line_number))

    sio.write("\n")

    error_code = error.get("error_code")
    if error_code is not None:
        sio.write("  Error code: {}\n".format(error_code))

    sio.write("  Message: " + error["message"] + "\n")

    context = error.get("context")
    if context is not None:
        sio.write("  Context:\n")
        for k, v in context.items():
            sio.write("    {}: {!r}\n".format(k, v))

    cause = error.get("cause")
    if cause is not None:
        sio.write("  Cause:\n")
        for cause_error in cause:
            sio.write("    - at path: {}\n".format(cause_error["path"]))
            sio.write("      message: {}\n".format(cause_error["message"]))
            sio.write("      value: {!r}\n".format(cause_error["value"]))

    return sio.getvalue()


def build_jsonschema_error(errors, base_path=[]):
    # From https://python-jsonschema.readthedocs.io/en/latest/errors/
    return [
        {
            "path": base_path + list(error.path),
            "message": error.message,
            "value": error.instance,
        }
        for error in sorted(errors, key=jsonschema.exceptions.relevance)
    ]


def category_tree_dataset_code_iter(category_tree):
    """Yield all dataset codes from a category_tree instance"""
    for elt in category_tree:
        if 'children' in elt:
            for dataset_code in category_tree_dataset_code_iter(elt['children']):
                yield dataset_code
        elif elt.get('code'):
            yield elt['code']


def validate_category_tree(storage, ignore_errors=[]):
    provider_code = storage.provider_code
    errors = []

    log.debug("Loading category_tree.json...")
    category_tree_json = storage.load_category_tree_json()
    if category_tree_json is not None:
        error_code = "category-tree-schema"
        if error_code not in ignore_errors:
            log.debug("Validating category_tree.json with JSON schema...")
            category_tree_schema_errors = list(validators.category_tree_validator.iter_errors(category_tree_json))
            if category_tree_schema_errors:
                errors.append({
                    "cause": build_jsonschema_error(category_tree_schema_errors),
                    "error_code": error_code,
                    "message": "Category tree does not conform to schema",
                    "provider_code": provider_code,
                    "location": "category_tree.json",
                })

    if category_tree_json is not None:
        dataset_codes_on_storage = set([dataset.dataset_code for dataset in storage.iter_datasets_dirs()])
        datasets_codes_in_category_tree = set(list(category_tree_dataset_code_iter(category_tree_json)))

        # Check that all datasets referenced in category_tree.json are present on disk
        error_code = "dataset-not-found-on-storage"
        if error_code not in ignore_errors:
            not_found_on_storage = datasets_codes_in_category_tree - dataset_codes_on_storage
            for dataset_code in not_found_on_storage:
                errors.append({
                    "error_code": error_code,
                    "message": "Dataset declared in category_tree.json is not found on storage",
                    "provider_code": provider_code,
                    "dataset_code": dataset_code,
                    "location": "category_tree.json"
                })

        # and all the datasets on disk are in the category_tree.json
        error_code = "dataset-not-found-in-category-tree"
        if error_code not in ignore_errors:
            not_found_in_category_tree = dataset_codes_on_storage - datasets_codes_in_category_tree
            for dataset_code in not_found_in_category_tree:
                # Load dataset.json
                try:
                    dataset_dir = storage.load_dataset_dir(dataset_code)
                    dataset_json = dataset_dir.load_dataset_json()
                except StorageError as exc:
                    errors.append({
                        **error_from_storage_error(exc),
                        "location": "{}/dataset.json".format(dataset_code),
                    })
                    continue
                else:
                    # Discontinued dataset, don't emit error
                    if dataset_json.get('discontinued'):
                        continue

                # Emits error
                errors.append({
                    "error_code": error_code,
                    "message": "Dataset found on storage is not declared in category_tree.json",
                    "provider_code": provider_code,
                    "dataset_code": dataset_code,
                    "location": "category_tree.json"
                })

    return errors


def validate_dataset(dataset_dir, ignore_errors=[]):
    errors = []
    provider_code = dataset_dir.storage.provider_code
    dataset_code = dataset_dir.dataset_code

    log.debug("Loading dataset.json...")
    try:
        dataset_json = dataset_dir.load_dataset_json()
    except StorageError as exc:
        errors.append({
            **error_from_storage_error(exc),
            "location": "{}/dataset.json".format(dataset_code),
        })
        return (None, None, errors)

    # Dataset directory name MUST be the dataset code.
    error_code = "invalid-dataset-directory-name"
    if error_code not in ignore_errors and dataset_json["code"] != dataset_code:
        errors.append({
            "error_code": error_code,
            "message": "Dataset code from dataset.json is different than the directory name",
            "context": {
                "dataset_json_code": dataset_json["code"],
                "directory_name": dataset_code,
            },
            "provider_code": provider_code,
            "dataset_code": dataset_code,
            "location": dataset_code,
        })

    dataset_series = dataset_json.pop("series", None)

    error_code = "dataset-schema"
    if error_code not in ignore_errors:
        log.debug("Validating dataset.json with JSON schema (except 'series' property)...")
        dataset_schema_errors = list(validators.dataset_validator.iter_errors(dataset_json))
        if dataset_schema_errors:
            errors.append({
                "cause": build_jsonschema_error(dataset_schema_errors),
                "error_code": error_code,
                "message": "Dataset does not conform to schema",
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "location": "{}/dataset.json".format(dataset_code),
            })

    return (dataset_json, dataset_series, errors)


def validate_provider(storage, ignore_errors=[], storage_dir_name=None):
    """Yield error dicts"""
    errors = []

    log.debug("Loading provider.json...")
    try:
        provider_json = storage.load_provider_json()
    except StorageError as exc:
        errors.append({
            **error_from_storage_error(exc),
            "location": "provider.json",
        })
        return (None, errors)

    provider_code = provider_json.get('code')

    error_code = "provider-schema"
    if error_code not in ignore_errors:
        log.debug("Validating provider.json with schema...")
        provider_schema_errors = list(validators.provider_validator.iter_errors(provider_json))
        if provider_schema_errors:
            errors.append({
                "cause": build_jsonschema_error(provider_schema_errors),
                "error_code": error_code,
                "message": "Provider does not conform to schema",
                "provider_code": provider_code,
                "location": "provider.json",
            })

    error_code = "invalid-provider-directory-name"
    if error_code not in ignore_errors:
        log.debug("Validating provider directory name...")
        error = validate_provider_directory_name(error_code, provider_code,
                                                 storage_dir_name=storage_dir_name)
        if error is not None:
            errors.append(error)

    return (provider_json, errors)


def validate_provider_directory_name(error_code, provider_code=None, storage_dir_name=None):
    if provider_code is None:
        log.debug("Skipped %r validator because provider_code could not be loaded", error_code)
        return None
    provider_code_lower = provider_code.lower()
    valid_directories_names = {
        "{}-json-data".format(provider_code_lower),
        "{}-json-data.git".format(provider_code_lower),
    }
    if storage_dir_name not in valid_directories_names:
        return {
            "error_code": error_code,
            "message": "Directory name is invalid",
            "context": {
                "directory_name": storage_dir_name,
                "valid_directories_names": valid_directories_names,
            },
            "provider_code": provider_code,
            "location": ".",
        }
    return None


def validate_observations(provider_code, dataset_code, series_code, location, observations, ignore_errors=[]):
    errors = []
    header = observations[0]
    header_nb_columns = len(header)
    rows = observations[1:]

    #
    # Header-level checks
    #

    # The two first columns of the header MUST be named `PERIOD` and `VALUE`.
    error_code = "invalid-observations-header"
    if error_code not in ignore_errors:
        if get(0, header, default=None) != "PERIOD":
            errors.append({
                "error_code": error_code,
                "message": "First column of header is not 'PERIOD'",
                "context": {
                    "header": header,
                },
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
                "line_number": 0,
            })

        if get(1, header, default=None) != "VALUE":
            errors.append({
                "error_code": error_code,
                "message": "Second column of header is not 'VALUE'",
                "context": {
                    "header": header,
                },
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
                "line_number": 0,
            })

    #
    # Column-level checks
    #

    # The `PERIOD` column MUST be sorted in an ascending order.
    error_code = "unordered-observations-periods"
    if error_code not in ignore_errors:
        periods = [row[0] for row in rows]
        if periods != sorted(periods):
            errors.append({
                "error_code": error_code,
                "message": "Values of the 'PERIOD' column are not sorted",
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
            })

    #
    # Row-level checks
    #

    if len(rows) == 0:

        error_code = "no-observations"
        if error_code not in ignore_errors:
            errors.append({
                "error_code": error_code,
                "message": "Time series has no observations",
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
            })

    previous_period_format = None

    for line_number, observation in enumerate(rows, start=2):
        nb_columns = len(observation)

        # Each row MUST have the same number of columns than the header.
        error_code = "invalid-observation-row-size"
        if error_code not in ignore_errors and nb_columns != header_nb_columns:
            errors.append({
                "error_code": error_code,
                "message": "Row has {} columns but header has {} columns".format(nb_columns, header_nb_columns),
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
                "line_number": line_number,
            })

        # The values of the `PERIOD` column:
        #   - MUST respect a specific format
        #   - MUST NOT include average values using `M13` or `Q5` periods
        period = observation[0]
        period_format = detect_period_format_strict(period)

        error_code_invalid = "invalid-observation-period-format"
        error_code_heterogeneous = "heterogeneous-observations-periods-formats"
        if error_code_invalid not in ignore_errors and period_format is None:
            errors.append({
                "error_code": error_code_invalid,
                "message": "Period format is invalid",
                "context": {
                    "period": period,
                },
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
                "line_number": line_number,
            })
        elif error_code_heterogeneous not in ignore_errors and \
                previous_period_format is not None and previous_period_format != period_format:
            errors.append({
                "error_code": error_code_heterogeneous,
                "message": "Period format is different than previous row",
                "context": {
                    "period_format": period_format,
                    "previous_period_format": previous_period_format,
                },
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": location,
                "line_number": line_number,
            })

        previous_period_format = period_format

        #  The values of the `VALUE` column MUST either be a float OR be `NA` meaning "not available".
        error_code = "invalid-observation-value"
        if error_code not in ignore_errors:
            value = observation[1]
            value_float = value_to_float(value)
            if value_float != NOT_AVAILABLE and not isinstance(value_float, float):
                errors.append({
                    "error_code": error_code,
                    "message": "Observation value is invalid",
                    "context": {
                        "value": value,
                    },
                    "provider_code": provider_code,
                    "dataset_code": dataset_code,
                    "series_code": series_code,
                    "location": location,
                    "line_number": line_number,
                })

    return errors


def validate_series(dataset_dir, dataset_series, ignore_errors=[], max_series=None, max_observations=None):
    errors = []
    provider_code = dataset_dir.storage.provider_code
    dataset_code = dataset_dir.dataset_code

    # Get series from `dataset.json` or `series.jsonl`.
    series_iterator = dataset_dir.iter_series_json(dataset_series=dataset_series)

    if dataset_series and isinstance(dataset_series, list):
        log.debug("Validating series from `dataset.json` with JSON schema...")
        base_path = ["series"]
        base_location = "{}/dataset.json#/series".format(dataset_code)
    else:
        log.debug("Validating series from `series.jsonl` with JSON schema...")
        base_path = []
        base_location = "{}/series.jsonl#".format(dataset_code)

        if dataset_series == []:
            error_code = "no-series"
            if error_code not in ignore_errors:
                errors.append({
                    "error_code": error_code,
                    "message": "Series list is empty in dataset.json",
                    "provider_code": provider_code,
                    "dataset_code": dataset_code,
                    "location": "{}/{}".format(dataset_code, 'dataset.json'),
                })

        elif dataset_series is None:
            series_jsonl_filepath = dataset_dir.path / 'series.jsonl'
            if not series_jsonl_filepath.exists():
                error_code = "no-series"
                if error_code not in ignore_errors:
                    errors.append({
                        "error_code": error_code,
                        "message": "No 'series' key in dataset.json but no series.jsonl file either",
                        "provider_code": provider_code,
                        "dataset_code": dataset_code,
                        "location": "{}/{}".format(dataset_code, 'dataset.json'),
                    })

    if max_series is not None:
        log.debug("Validating %d series max", max_series)
        series_iterator = take(max_series, series_iterator)

    validated_series_codes = set()
    validated_series_names = set()
    observations_series_codes = []

    for index, series_json in enumerate(series_iterator):
        series_code = series_json["code"]
        series_name = series_json.get("name")
        series_id_str = dataset_dir.series_id_str(series_code)
        log.debug("Validating series %r...", series_id_str)

        error_code = "invalid-series-code"
        if error_code not in ignore_errors:
            series_schema_errors = list(validators.series_validator.iter_errors(series_json))
            if series_schema_errors:
                errors.append({
                    "cause": build_jsonschema_error(series_schema_errors, base_path),
                    "error_code": error_code,
                    "message": "Series code does not conform to schema",
                    "provider_code": provider_code,
                    "dataset_code": dataset_code,
                    "series_code": series_code,
                    "location": "{}/{}".format(base_location, index),
                })

        error_code = "duplicated-series-code"
        if error_code not in ignore_errors and series_code in validated_series_codes:
            errors.append({
                "error_code": error_code,
                "message": "Series code already met before",
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": "{}/{}".format(base_location, index),
            })

        error_code = "duplicated-series-name"
        if error_code not in ignore_errors and series_name is not None and series_name in validated_series_names:
            errors.append({
                "error_code": error_code,
                "message": "Series name already met before",
                "context": {
                    "series_name": series_name,
                },
                "provider_code": provider_code,
                "dataset_code": dataset_code,
                "series_code": series_code,
                "location": "{}/{}".format(base_location, index),
            })

        observations = series_json.get("observations")
        if observations is None:
            # Validate observations in TSV files later.
            observations_series_codes.append(series_code)
        else:
            # Validate observations in series JSON lines file now, to avoid loading them again later.
            series_jsonl_file_name = dataset_dir.get_series_jsonl_file_name(dataset_series=dataset_series)
            if series_jsonl_file_name is None:
                error_code = "unsupported-observations-in-dataset-json"
                if error_code not in ignore_errors:
                    errors.append({
                        "error_code": error_code,
                        "message": "Having observations in 'series' property of dataset.json is not supported",
                        "provider_code": provider_code,
                        "dataset_code": dataset_code,
                        "series_code": series_code,
                        "location": "{}/dataset.json".format(dataset_code),
                    })
            else:
                series_file_path = dataset_dir.path / series_jsonl_file_name
                log.debug("Validating observations (in JSON lines format) of series %r...", series_id_str)
                location = str(series_file_path.relative_to(dataset_dir.storage.path))
                observations_errors = validate_observations(
                    provider_code, dataset_code, series_code, location, observations,
                    ignore_errors=ignore_errors)
                errors.extend(observations_errors)

        validated_series_codes.add(series_code)
        validated_series_names.add(series_name)

    if observations_series_codes:
        log.debug("Validating observations (in TSV format) of %d series...", len(observations_series_codes))

        observations_iterator = dataset_dir.iter_observations(observations_series_codes)

        if max_observations is not None:
            log.debug("Validating %d observations max", max_observations)
            observations_iterator = take(max_observations, observations_iterator)

        for _, series_code, observations in observations_iterator:
            series_id_str = dataset_dir.series_id_str(series_code)
            log.debug("Validating observations of series %r...", series_id_str)
            tsv_filepath = dataset_dir.storage.path / '{}.tsv'.format(series_code)
            location = str(tsv_filepath.relative_to(dataset_dir.storage.path))
            observations_errors = validate_observations(
                provider_code, dataset_code, series_code, location, observations,
                ignore_errors=ignore_errors)
            errors.extend(observations_errors)

    return errors


if __name__ == '__main__':
    sys.exit(main())
