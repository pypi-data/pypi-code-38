# Copyright 2018 Catalyst IT Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

from rt_client.common import utils


class TestUtils(unittest.TestCase):
    def test_build_field_query(self):

        queries = [
            ("FieldA", {"fields": "FieldA"}),
            (["FieldA", "FieldB", "FieldC"], {"fields": "FieldA,FieldB,FieldC"}),
            (
                {"FieldA": {"SubfieldA": "Sub-subfieldA"}},
                {"fields[FieldA][SubfieldA]": "Sub-subfieldA"},
            ),
            (
                {"FieldA": ["SubfieldA", "SubfieldB"]},
                {"fields[FieldA]": "SubfieldA,SubfieldB"},
            ),
            (
                {"FieldA": {"SubfieldA": {"Sub-subfieldA": "Sub-sub-subfieldA"}}},
                {"fields[FieldA][SubfieldA][Sub-subfieldA]": "Sub-sub-subfieldA"},
            ),
            (
                {
                    "FieldA": {
                        "SubfieldA": {
                            "Sub-subfieldA": ["Sub-sub-subfieldA", "Sub-sub-subfieldB"]
                        }
                    }
                },
                {
                    "fields[FieldA][SubfieldA][Sub-subfieldA]": "Sub-sub-subfieldA,Sub-sub-subfieldB" # noqa
                },
            ),
            (
                {
                    "FieldA": {"SubfieldA": {"Sub-subfieldA": "Sub-sub-subfieldA"}},
                    "FieldB": {"SubfieldB": {"Sub-subfieldB": "Sub-sub-subfieldB"}},
                },
                {
                    "fields[FieldA][SubfieldA][Sub-subfieldA]": "Sub-sub-subfieldA",
                    "fields[FieldB][SubfieldB][Sub-subfieldB]": "Sub-sub-subfieldB",
                },
            ),
            (
                ["FieldA", "FieldB", {"FieldC": {"SubfieldC": "Sub-subfieldC"}}],
                {
                    "fields": "FieldA,FieldB",
                    "fields[FieldC][SubfieldC]": "Sub-subfieldC",
                },
            ),
            (
                [
                    "FieldA",
                    {"FieldB": {"SubfieldB": "Sub-subfieldB"}},
                    {"FieldC": {"SubfieldC": "Sub-subfieldC"}},
                ],
                {
                    "fields": "FieldA",
                    "fields[FieldB][SubfieldB]": "Sub-subfieldB",
                    "fields[FieldC][SubfieldC]": "Sub-subfieldC",
                },
            ),
            (
                [
                    "FieldA",
                    "FieldB,FieldD,FieldE",
                    {"FieldC": {"SubfieldC": "Sub-subfieldC"}},
                ],
                {
                    "fields": "FieldA,FieldB,FieldD,FieldE",
                    "fields[FieldC][SubfieldC]": "Sub-subfieldC",
                },
            ),
            (
                [
                    ["FieldA", "FieldB", "FieldD", "FieldE"],
                    {"FieldC": {"SubfieldC": "Sub-subfieldC"}},
                ],
                {
                    "fields": "FieldA,FieldB,FieldD,FieldE",
                    "fields[FieldC][SubfieldC]": "Sub-subfieldC",
                },
            ),
        ]

        for query, expected in queries:
            self.assertEqual(utils.build_fields_query(query), expected)
