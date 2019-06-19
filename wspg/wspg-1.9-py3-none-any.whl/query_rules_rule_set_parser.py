#
#   Copyright 2018 University of Lancaster
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from psycopg2 import sql  # type: ignore

import jquery_querybuilder_psycopg2  # type: ignore


class QueryRulesRuleSetParser(jquery_querybuilder_psycopg2.BaseRuleSetParser):  # type: ignore
    #
    # PostgreSQL standard comparison functions (section 9.2)
    #
    equal_to_operator = "{field} = {value}"

    less_than_operator = "{field} < {value}"
    less_than_or_equal_to_operator = "{field} <= {value}"
    greater_than_operator = "{field} > {value}"
    greater_than_or_equal_to_operator = "{field} >= {value}"

    @staticmethod
    def between_operator(field, value):  # type: ignore
        if not isinstance(value, list) or not len(value) == 2:
            raise jquery_querybuilder_psycopg2.ParseError(
                "Value for 'between' operator must be a list of two items")

        return sql.SQL("{field} BETWEEN {low_value} AND {high_value}").format(
            field=field, low_value=sql.Literal(value[0]),
            high_value=sql.Literal(value[1]))

    is_null_operator = "{field} IS NULL"
    is_not_null_operator = "{field} IS NOT NULL"

    is_true_operator = "{field} IS TRUE"
    is_not_true_operator = "{field} IS NOT TRUE"

    is_false_operator = "{field} IS FALSE"
    is_not_false_operator = "{field} IS NOT FALSE"

    #
    # String (section 9.4)
    #
    string_case_insensitive_equal_to_operator = "lower({field}::text) = lower({value})"

    #
    # Pattern Matching (section 9.7)
    #
    string_like_operator = "{field}::text LIKE {value}"
    string_ilike_operator = "{field}::text ILIKE {value}"

    #
    # Network Address (section 9.12)
    #
    inet_is_contained_by_operator = "{field}::inet << {value}"
    inet_is_contained_by_or_equal_to_operator = "{field}::inet <<= {value}"

    inet_contains_operator = "{field}::inet >> {value}"
    inet_contains_or_equal_to_operator = "{field}::inet >>= {value}"
