# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test helpers."""

import pytest
from invenio_pidstore.fetchers import FetchedPID
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.recordid import RecordIdProvider
from marshmallow import Schema, fields

from invenio_pidrelations.serializers.utils import serialize_relations


def pid_to_fetched_recid(pid):
    """Build a fetched recid from a PersistentIdentifier."""
    return FetchedPID(
        provider=RecordIdProvider,
        pid_type=RecordIdProvider.pid_type,
        pid_value=pid.pid_value,
    )


with_pid_and_fetched_pid = pytest.mark.parametrize("build_pid", [
    (lambda pid: pid),
    # test with a fetched PID
    (lambda pid: pid_to_fetched_recid(pid)),
])
"""Decorator used to test with real PersistentIdentifier and fetched PID."""


def create_pids(number, prefix='', status=PIDStatus.REGISTERED):
    """Create a give'n number of PIDs.

    :param number: number of PIDs to create.
    """
    return [PersistentIdentifier.create(
        'recid', '{0}_pid_value_{1}_{2}'.format(prefix, status, p),
        object_type='rec', status=status) for p in range(number)]


def filter_pids(pids, status):
    """Filter PIDs based on their status."""
    return [p for p in pids if p.status == status]


def compare_dictionaries(dict1, dict2):
    """Assert two dicts are equal."""
    if dict1 is None or dict2 is None:
        return False

    if type(dict1) is not dict or type(dict2) is not dict:
        return False

    shared_keys = set(dict2.keys()) & set(dict2.keys())

    if not (len(shared_keys) == len(dict1.keys()) and
            len(shared_keys) == len(dict2.keys())):
        return False

    dicts_are_equal = True
    for key in dict1.keys():
        if type(dict1[key]) is dict:
            dicts_are_equal = dicts_are_equal and \
                compare_dictionaries(dict1[key], dict2[key])
        else:
            dicts_are_equal = dicts_are_equal and (dict1[key] == dict2[key])
    return dicts_are_equal


class PIDRelationsMixin(object):
    """Mixin for easy inclusion of relations information in Record schemas."""

    relations = fields.Method('dump_relations')

    def dump_relations(self, obj):
        """Dump the relations to a dictionary."""
        pid = self.context['pid']
        return serialize_relations(pid)
