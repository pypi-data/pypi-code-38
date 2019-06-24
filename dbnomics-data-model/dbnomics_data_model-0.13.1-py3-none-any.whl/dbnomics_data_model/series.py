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


"""Functions manipulating time series metadata in JSON format."""

import logging

log = logging.getLogger(__name__)


def generate_series_name(dimensions, dimensions_codes_order, dimensions_values_labels):
    """Generate a name for a time series based on dimensions values labels.

    >>> generate_series_name({}, [], {})
    ''
    >>> generate_series_name({'FREQ': 'A'}, [], {})
    ''
    >>> generate_series_name({}, [], {'FREQ': {'A': 'Annual'}})
    ''
    >>> generate_series_name({}, ['FREQ'], {})
    'FREQ (MISSING CODE)'
    >>> generate_series_name({'FREQ': 'A'}, ['FREQ'], {'FREQ': {'A': 'Annual'}})
    'Annual'
    >>> generate_series_name({'FREQ': 'M'}, ['FREQ'], {'FREQ': {'A': 'Annual'}})
    'M'
    >>> generate_series_name({'FREQ': 'A', 'INDICATOR': 'X'}, ['FREQ', 'INDICATOR'], {'FREQ': {'A': 'Annual'}, 'INDICATOR': {'X': 'Files'}})
    'Annual – Files'
    >>> generate_series_name({'FREQ': 'A', 'INDICATOR': 'X'}, ['FREQ', 'INDICATOR'], {'FREQ': {'A': 'Annual'}, 'INDICATOR': {'X': 'Files', 'Y': 'Directories'}})
    'Annual – Files'

    # Duplicate dimensions values labels
    >>> generate_series_name({'FREQ': 'A', 'INDICATOR': 'X'}, ['FREQ', 'INDICATOR'], {'FREQ': {'A': 'Annual'}, 'INDICATOR': {'X': 'Files', 'Y': 'Files'}})
    'Annual – Files (X)'
    >>> generate_series_name({'FREQ': 'A', 'INDICATOR': 'Z'}, ['FREQ', 'INDICATOR'], {'FREQ': {'A': 'Annual'}, 'INDICATOR': {'X': 'Files', 'Y': 'Files'}})
    'Annual – Z'
    """
    def get_dimension_value_label(dimension_code):
        dimension_value_code = dimensions.get(dimension_code)
        if dimension_value_code is None:
            log.error("Missing dimension value code in Solr series for dimension_code {}: {}".format(
                dimension_code, dimensions))
            return "{} (MISSING CODE)".format(dimension_code)
        dimension_values_labels = dimensions_values_labels.get(dimension_code, {})
        dimension_value_label = dimension_values_labels.get(dimension_value_code)
        if dimension_value_label is None:
            dimension_value_label = dimension_value_code
        else:
            if len([
                v for v in dimension_values_labels.values()
                if v == dimension_value_label
            ]) > 1:
                dimension_value_label += ' ({})'.format(dimension_value_code)
        return dimension_value_label

    series_name = " – ".join(map(get_dimension_value_label, dimensions_codes_order))
    return series_name


def series_ids_to_tree(series_ids):
    """Convert a list of `series_ids` tuples to a `dict[dict[list[str]]]`, indexed by `provider_code`
    then `dataset_code`.

    Example:
    >>> def to_pairs(d):
    ...     return sorted((k, to_pairs(v)) for k, v in d.items()) if isinstance(d, dict) else d
    >>> to_pairs(series_ids_to_tree([ \
        ('p1', 'd1', 's1'), ('p1', 'd1', 's2'), ('p1', 'd2', 's1'), ('p2', 'd1', 's1')]))
    [('p1', [('d1', ['s1', 's2']), ('d2', ['s1'])]), ('p2', [('d1', ['s1'])])]
    """
    tree = {}
    for (provider_code, dataset_code, series_code) in series_ids:
        tree.setdefault(provider_code, {}).setdefault(dataset_code, []).append(series_code)
    return tree
