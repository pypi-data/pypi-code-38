# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PIDRelation JSON Schema for metadata."""

from marshmallow import Schema, fields

from ..api import PIDNodeOrdered
from ..config import RelationType
from ..utils import resolve_relation_type_config


class PIDSchema(Schema):
    """PID schema."""

    pid_type = fields.String()
    pid_value = fields.String()


class RelationSchema(Schema):
    """Generic PID relation schema."""

    # NOTE: Maybe do `fields.Function` for all of these and put them in `utils`
    parent = fields.Method('dump_parent')
    children = fields.Method('dump_children')
    type = fields.Method('dump_type')
    is_ordered = fields.Boolean()
    is_parent = fields.Method('_is_parent')
    is_child = fields.Method('_is_child')
    is_last = fields.Method('dump_is_last')
    index = fields.Method('dump_index')
    next = fields.Method('dump_next')
    previous = fields.Method('dump_previous')

    def _dump_relative(self, relative):
        if relative:
            data, errors = PIDSchema().dump(relative)
            return data
        else:
            return None

    def dump_next(self, obj):
        """Dump the parent of a PID."""
        if self._is_child(obj) and not obj.is_last_child(self.context['pid']):
            return self._dump_relative(obj.next_child(self.context['pid']))

    def dump_previous(self, obj):
        """Dump the parent of a PID."""
        if self._is_child(obj) and obj.index(self.context['pid']) > 0:
            return self._dump_relative(obj.previous_child(self.context['pid']))

    def dump_index(self, obj):
        """Dump the index of the child in the relation."""
        if isinstance(obj, PIDNodeOrdered) and self._is_child(obj):
            return obj.index(self.context['pid'])
        else:
            return None

    def _is_parent(self, obj):
        """Check if the PID from the context is the parent in the relation."""
        return self.context['pid'] == obj.pid

    def _is_child(self, obj):
        """Check if the PID from the context is the child in the relation."""
        return self.context['pid'] in obj.children.all()

    def dump_is_last(self, obj):
        """Dump the boolean stating if the child in the relation is last.

        Dumps `None` for parent serialization.
        """
        if self._is_child(obj) and isinstance(obj, PIDNodeOrdered):
            if obj.children.count() > 0:
                return obj.children.ordered('asc').all()[-1] == \
                    self.context['pid']
            elif obj.draft_child:
                return obj.draft_child == self.context['pid']
            else:
                return True
        else:
            return None

    def dump_type(self, obj):
        """Dump the text name of the relation."""
        if not isinstance(obj.relation_type, RelationType):
            return resolve_relation_type_config(obj.relation_type).name
        else:
            return obj.relation_type.name

    def dump_parent(self, obj):
        """Dump the parent of a PID."""
        if not self._is_parent(obj):
            return self._dump_relative(obj.pid)
        return None

    def dump_children(self, obj):
        """Dump the siblings of a PID."""
        data, errors = PIDSchema(many=True).dump(
            obj.children.ordered('asc').all())
        return data
