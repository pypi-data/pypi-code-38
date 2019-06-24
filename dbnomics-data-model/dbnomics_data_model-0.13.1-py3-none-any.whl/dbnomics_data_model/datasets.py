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
import logging
from collections import OrderedDict

"""Functions manipulating datasets metadata in JSON format."""

log = logging.getLogger(__name__)


def get_dimensions_codes_order(dataset_json):
    """Try to get dimensions codes order from `dataset.json` properties, with 2 fallbacks."""
    return dataset_json.get("dimensions_codes_order") or \
        sorted(dataset_json.get("dimensions_labels", {}).keys()) or \
        sorted(dataset_json.get("dimensions_values_labels", {}).keys())


def get_dimensions_values_labels(dataset_json):
    """Get dimensions values labels from `dataset.json` properties
        Normalising tuple list values as dict (default) or OrderedDict
        (form tuple list values)

        # No dimensions_values_labels declared
        >>> get_dimensions_values_labels({})
        {}

        # Unsorted dimension values
        >>> get_dimensions_values_labels({'dimensions_values_labels':{'freq':{'A':'Annual','Q':'Quarterly'}}})['freq'].get('A')
        'Annual'

        # Sorted dimension values
        >>> get_dimensions_values_labels({'dimensions_values_labels':{'geo':[['FR','France'],['SE','Sweden'],['RE','Rest of Europe']]}})['geo'].items()
        odict_items([('FR', 'France'), ('SE', 'Sweden'), ('RE', 'Rest of Europe')])

        # Missing level of dict
        >>> get_dimensions_values_labels({'dimensions_values_labels':{'A':'Annual','Q':'Quarterly'}})
        {}
    """
    def iter_dimensions_values_labels():
        for k, v in dim_val_labels.items():
            if isinstance(v, dict):
                yield (k, v)
            elif isinstance(v, list):
                yield (k, OrderedDict(v))
            else:
                log.error("Wrong datatype [{}]".format(type(v)))

    dim_val_labels = dataset_json.get("dimensions_values_labels")
    if not dim_val_labels:
        return {}
    return dict(iter_dimensions_values_labels())
