import importlib.util
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import importlib_resources
import requests
import toml
from toolz import get_in, thread_first, update_in

import goodtables
import tableschema

from . import csv_helpers, loaders, messages
from .spec import spec

log = logging.getLogger(__name__)

VALIDATA_MAX_ROWS = 100000


def import_custom_checks():
    """Import all custom checks classes"""
    with importlib_resources.path('validata_core', 'custom_checks') as cs_dir:
        for check_file in cs_dir.glob('*.py'):
            spec = importlib.util.spec_from_file_location(check_file.stem, str(check_file))
            if spec is None:
                log.error('spec is None for %r', str(check_file))
            else:
                foo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(foo)


import_custom_checks()


def replace_at(seq, index, item):
    """Replace seq[index] by item."""
    return (
        item if index == index1 else item1
        for index1, item1 in enumerate(seq)
    )


def add_error(report, table_index, error):
    return update_in(report, ["tables"], lambda tables: list(
        replace_at(tables, table_index, thread_first(
            tables[table_index],
            (update_in, ["errors"], lambda errors: [error] + errors),
            (update_in, ["error-count"], lambda error_count: error_count + 1),
        ))))


def improve_messages(report, schema):
    """Translate report error messages and add `title` and `content` fields"""
    if report is None:
        return None

    for table_id in range(report['table-count']):

        table = report['tables'][table_id]
        table['errors'] = messages.improve_messages(table['errors'], schema)

    return report


def compute_error_statistics(errors):
    """Computes error statistics as a dict:
    {
        'count': 12,
        'structure-errors': {
            'count': 1,
            'count-by-code': {
                'invalid-column-delimiter': 1
            }
        },
        'value-errors': {
            'count': 10,
            'rows-count': 3,
            'count-by-code': {
                'type-or-format-error': 2,
                'pattern-constraint': 7,
                'french-siret-value': 1,
            }
        },
    }
    """

    # Nb of errors by category
    errors_nb_dict = {'structure': 0, 'value': 0}

    # Errors distribution by category
    errors_dist_dict = {'structure': defaultdict(int), 'value': defaultdict(int)}

    # Fill in error stats
    for err in errors:
        err_tag = err['tag']
        errors_nb = len(err['message-data']['headers']) \
            if err['code'] in ('extra-headers', 'missing-headers') else 1
        errors_nb_dict[err_tag] += errors_nb
        errors_dist_dict[err_tag][err['code']] += errors_nb

    # Compute statistics
    return {
        'structure-errors': {
            'count': errors_nb_dict['structure'],
            'count-by-code': errors_dist_dict['structure'],
        },
        'value-errors': {
            'count': errors_nb_dict['value'],
            'rows-count': len(set([err['row-number'] for err in errors if err['tag'] == 'value'])),
            'count-by-code': errors_dist_dict['value'],
        },
        'count': errors_nb_dict['structure'] + errors_nb_dict['value']
    }


def amend_report(report):
    """tag 'structure' and 'value' error
    Remove 'value' errors if 'structure' errors
    Computes statistics
    """

    def categorize_err(err):
        """Computes error category: 'structure' or 'value'"""
        if err.get('column-number') is None and err.get('row-number') is None:
            return 'structure'
        return 'value'

    # Tag 'structure' or 'value'
    errors = [{**err, 'tag': categorize_err(err)} for err in report['tables'][0]['errors']]

    # Remove 'value' errors if 'structure' errors other than 'invalid-column-delimiter'
    if any([err['tag'] == 'structure' and err['code'] != 'invalid-column-delimiter' for err in errors]):
        errors = [err for err in errors if err['tag'] != 'value']

    # Among value errors, only keep a single error by error cell
    # => the 1st encountered one
    filtered_errors = []
    row_col_set = set()
    for err in errors:
        if err['tag'] == 'value':
            row_col_id = '{}_{}'.format(err['row-number'], err.get('column-number', ''))
            if row_col_id in row_col_set:
                continue
            row_col_set.add(row_col_id)
        filtered_errors.append(err)
    errors = filtered_errors

    # Integrate enhanced errors into report
    report['tables'][0]['errors'] = errors
    report['tables'][0]['error-count'] = len(errors)

    # Store statistics
    stats = compute_error_statistics(errors)
    report['tables'][0]['error-stats'] = stats

    return report

# Error raised when goodtables return no 'headers' information in report
# Validata can't go further in this case


class MissingHeaderError(Exception):
    pass


class Validator:
    def load_schema(self, source):
        """Return a `tableschema.Schema` instance from `source`."""
        if isinstance(source, Path):
            source = str(source)
        try:
            return tableschema.Schema(source)
        except tableschema.exceptions.LoadError as e:
            log.exception(e)
            log.warning("Schema load exception from {}".format(source))
            return None

    def validate(self, source, schema, **options):
        """Validate a `source` using a `schema`.

        `schema` can be either:
        - a `pathlib.Path`
        - a `str` containing either:
            - a file path
            - an URL
        - a `dict` representing the schema in JSON
        - a `tableschema.Schema` instance
        """
        if not isinstance(schema, tableschema.Schema):
            schema = self.load_schema(schema)
        schema_descriptor = schema.descriptor

        checks = ['structure', 'schema', {'extra-or-missing-header': {}}]
        custom_checks_config = schema_descriptor.get('custom_checks')
        if custom_checks_config:
            for custom_check_conf in custom_checks_config:
                checks.append({custom_check_conf['name']: custom_check_conf['params']})

        inspector = goodtables.Inspector(
            checks=checks,
            skip_checks=['non-matching-header', 'extra-header', 'missing-header'],
            row_limit=VALIDATA_MAX_ROWS,
        )
        options = {**options, "custom_loaders": loaders.custom_loaders}
        report = inspector.inspect(source=source, schema=schema_descriptor, **options)

        # Goodtables return no 'headers' information :-(
        if not report['tables'][0].get('headers'):
            raise MissingHeaderError()

        if report['tables'][0].get('format') == "csv" and not any(
            get_in(['errors', err['code'], 'type'], spec, default=None) == 'source'
            for err in report['tables'][0]['errors']
        ):
            standard_csv_delimiter = ","
            detected_delimiter = csv_helpers.detect_dialect(source, **options).delimiter
            if detected_delimiter != standard_csv_delimiter:
                error = goodtables.Error(
                    code='invalid-column-delimiter',
                    message_substitutions={
                        "detected": detected_delimiter,
                        "expected": standard_csv_delimiter,
                    },
                )
                report = add_error(report, table_index=0, error=dict(error))

        # Translate error messages
        report = improve_messages(report, schema_descriptor)

        # Tag errors ('structure' or 'value')
        # Compute statistics
        report = amend_report(report)

        # Add date
        report['date'] = datetime.now(timezone.utc).isoformat()

        return report


def compute_badge(report, config) -> dict:
    """Compute badge from report statistics and badge configuration."""

    def build_badge(structure_status, body_status=None, error_ratio=None):
        """Badge info creation"""
        if structure_status == 'KO':
            return {
                "structure": 'KO'
            }
        return {
            "structure": structure_status,
            "body": body_status,
            "error-ratio": error_ratio
        }

    # Gets stats from report
    stats = report['tables'][0]['error-stats']

    # And total number of cells
    column_count = len(report['tables'][0]['headers'])
    row_count = report['tables'][0]['row-count']
    cell_total_number = column_count * row_count

    # No errors
    if stats['count'] == 0:
        return build_badge('OK', 'OK', 0.0)

    # Structure part
    structure_status = None
    if stats['structure-errors']['count'] == 0:
        structure_status = 'OK'
    else:
        cbc = stats['structure-errors']['count-by-code']
        if len(cbc) == 1 and 'invalid-column-delimiter' in cbc:
            structure_status = 'WARN'
        else:
            # structure_status = 'KO'
            return build_badge('KO')

    # body part
    value_errors = stats['value-errors']
    if value_errors['count'] == 0:
        return build_badge(structure_status, 'OK', 0.0)

    # Computes error ratio
    weight_dict = config['body']['errors-weight']
    ratio = sum([nb * weight_dict.get(err, 1.0) for err, nb in value_errors['count-by-code'].items()]) \
        / cell_total_number
    body_status = 'WARN' if ratio < config['body']['acceptability-threshold'] else 'KO'

    return build_badge(structure_status, body_status, ratio)
