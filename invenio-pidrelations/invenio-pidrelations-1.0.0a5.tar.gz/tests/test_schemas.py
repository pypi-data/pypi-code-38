# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schema tests."""

from marshmallow import Schema
from test_helpers import PIDRelationsMixin


class SampleRecordSchema(Schema, PIDRelationsMixin):
    """Sample record schema."""
    pass


def test_schema(app, nested_pids_and_relations):
    """Test the marshmallow schema serialization."""
    schema = SampleRecordSchema(strict=True)

    pids, exp_relations = nested_pids_and_relations
    for p_idx in exp_relations.keys():
        pid = pids[p_idx]
        expected = exp_relations[p_idx]
        input_data = {'pid': pid}
        schema.context['pid'] = pid
        data, errors = schema.dump(input_data)
        assert not errors
        assert expected == data  # Test against hand-crafted fixture
    pass


def test_custom_schema(app, nested_pids_and_relations, custom_relation_schema):
    """Test the marshmallow schema serialization with custom schema."""
    schema = SampleRecordSchema(strict=True)
    pids, exp_relations = nested_pids_and_relations

    pid = pids[4]
    input_data = {'pid': pid}
    schema.context['pid'] = pid
    data, errors = schema.dump(input_data)
    expected = {
        'relations': {
            'version': [
                {
                    'children': [{'pid_type': 'recid', 'pid_value': '2'},
                                 {'pid_type': 'recid', 'pid_value': '3'},
                                 {'pid_type': 'recid', 'pid_value': '4'}],
                    'has_three_children': True,
                },
            ],
            # 'ordered': [
            #     {
            #         'children': [{'pid_type': 'recid', 'pid_value': '6'},
            #                      {'pid_type': 'recid', 'pid_value': '4'},
            #                      {'pid_type': 'recid', 'pid_value': '7'}],
            #         'has_three_children': True,
            #     },
            #     {
            #         'children': [{'pid_type': 'recid', 'pid_value': '8'},
            #                      {'pid_type': 'recid', 'pid_value': '9'}],
            #         'has_three_children': False,
            #     },
            # ],
            # 'unordered': [
            #     {
            #         'children': [{'pid_type': 'recid', 'pid_value': '4'},
            #                      {'pid_type': 'recid', 'pid_value': '11'}],
            #         'has_three_children': False,
            #     },
            # ],
        }
    }
    assert not errors
    assert expected == data
