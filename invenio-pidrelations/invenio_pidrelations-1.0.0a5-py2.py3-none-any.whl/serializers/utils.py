# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PIDRelation serialization utilities."""

from invenio_pidrelations.api import PIDRelation

from ..utils import resolve_relation_type_config


def serialize_relations(pid):
    """Serialize the relations for given PID."""
    data = {}
    relations = PIDRelation.get_child_relations(pid).all()
    for relation in relations:
        rel_cfg = resolve_relation_type_config(relation.relation_type)
        dump_relation(rel_cfg.api(relation.parent),
                      rel_cfg, pid, data)
    parent_relations = PIDRelation.get_parent_relations(pid).all()
    rel_cfgs = set([resolve_relation_type_config(p) for p in parent_relations])
    for rel_cfg in rel_cfgs:
        dump_relation(rel_cfg.api(pid), rel_cfg, pid, data)
    return data


def dump_relation(api, rel_cfg, pid, data):
    """Dump a specific relation to a data dict."""
    schema_class = rel_cfg.schema
    if schema_class is not None:
        schema = schema_class()
        schema.context['pid'] = pid
        result, errors = schema.dump(api)
        data.setdefault(rel_cfg.name, []).append(result)
