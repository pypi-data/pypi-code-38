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


"""JSON schema functions"""


import pkgutil

import jsonschema

import ujson as json


def load_schema(json_file_name):
    json_schema_str = pkgutil.get_data("dbnomics_data_model", "schemas/{}".format(json_file_name)).decode('utf-8')
    return json.loads(json_schema_str)


category_tree_schema = load_schema("category_tree.json")
dataset_schema = load_schema("dataset.json")
definitions_schema = load_schema("definitions.json")
provider_schema = load_schema("provider.json")
series_schema = load_schema("series.json")

# Apparently definitions.json has to be defined twice, otherwise it is not found sometimes.
store = {
    "definitions.json": definitions_schema,
    "/definitions.json": definitions_schema,
    "series.json": series_schema,
}

format_checker = jsonschema.FormatChecker()

provider_validator = jsonschema.Draft4Validator(
    provider_schema,
    format_checker=format_checker,
    resolver=jsonschema.RefResolver.from_schema(provider_schema, store=store),
)
category_tree_validator = jsonschema.Draft4Validator(
    category_tree_schema,
    format_checker=format_checker,
    resolver=jsonschema.RefResolver.from_schema(category_tree_schema, store=store),
)
dataset_validator = jsonschema.Draft4Validator(
    dataset_schema,
    format_checker=format_checker,
    resolver=jsonschema.RefResolver.from_schema(dataset_schema, store=store),
)
series_validator = jsonschema.Draft4Validator(
    series_schema,
    format_checker=format_checker,
    resolver=jsonschema.RefResolver.from_schema(series_schema, store=store),
)
