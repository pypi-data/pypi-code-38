# -*- coding:utf-8 -*-
from collections import OrderedDict

from django.utils.encoding import force_text
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import RelatedField, SlugRelatedField, ManyRelatedField

from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework import exceptions
from rest_framework.request import clone_request
from ..utils.modelutils import get_model_dependants

__author__ = 'denishuang'


class RelatedChoicesMetadata(SimpleMetadata):
    def determine_metadata(self, request, view):
        metadata = super(RelatedChoicesMetadata, self).determine_metadata(request, view)
        metadata['dependencies'] = self.get_dependencies(metadata)
        return metadata

    def get_dependencies(self, metadata):
        return [
            f.get('model')
            for f in metadata.get('actions', {}).get('POST', {}).values()
            if f.get('model')
        ]

    def get_field_info(self, field):
        field_info = super(RelatedChoicesMetadata, self).get_field_info(field)
        if not field_info.get('read_only') and isinstance(field, (RelatedField, ManyRelatedField)):
            field_info = self.add_related_field_info(field, field_info)
        return field_info

    def add_related_field_info(self, field, field_info):
        if isinstance(field, ManyRelatedField):
            field = field.child_relation
            field_info['multiple'] = True
        if not hasattr(field, "queryset") or field.queryset is None:
            return field_info
        qset = field.queryset
        field_info['model'] = qset.model._meta.label_lower
        return field_info

    def determine_actions(self, request, view):
        actions = super(RelatedChoicesMetadata, self).determine_actions(request, view)
        view.request = clone_request(request, 'GET')
        try:
            # Test global permissions
            if hasattr(view, 'check_permissions'):
                view.check_permissions(view.request)
        except (exceptions.APIException, PermissionDenied, Http404):
            pass
        else:

            search_fields = getattr(view, 'search_fields', [])
            from ..utils import modelutils
            cf = lambda f: f[0] in ['^', '@', '='] and f[1:] or f
            actions['SEARCH'] = search = {}
            search['search_fields'] = [modelutils.get_related_field_verbose_name(view.queryset.model, cf(f)) for f in
                                       search_fields]
            from django_tables2.utils import A
            ffs = A('filter_class._meta.fields').resolve(view, quiet=True) or getattr(view, 'filter_fields', [])
            search['filter_fields'] = isinstance(ffs, dict) and ffs.keys() or ffs
            search['ordering_fields'] = getattr(view, 'ordering_fields', [])
            serializer = view.get_serializer()
            actions['LIST'] = self.get_list_info(serializer)
        finally:
            view.request = request
        return actions

    def get_list_info(self, serializer):
        if hasattr(serializer, 'child'):
            # If this is a `ListSerializer` then we want to examine the
            # underlying child serializer instance instead.
            serializer = serializer.child
        return OrderedDict(
            [
                (field_name, self.get_list_field_info(field))
                for field_name, field in serializer.fields.items()
            ]
        )

    def get_list_field_info(self, field):
        field_info = OrderedDict()
        field_info['type'] = self.label_lookup[field]

        attrs = ['label', ]

        for attr in attrs:
            value = getattr(field, attr, None)
            if value is not None and value != '':
                field_info[attr] = force_text(value, strings_only=True)

        if getattr(field, 'child', None):
            field_info['child'] = self.get_list_field_info(field.child)
        elif getattr(field, 'fields', None):
            field_info['children'] = self.get_list_info(field)
        from rest_framework import serializers
        if isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)):
            field_info = self.add_related_field_info(field, field_info)
        elif hasattr(field, 'choices'):
            field_info['choices'] = [
                {
                    'value': choice_value,
                    'display_name': force_text(choice_name, strings_only=True)
                }
                for choice_value, choice_name in field.choices.items()
            ]

        return field_info


class RelatedSlugMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(RelatedSlugMetadata, self).get_field_info(field)

        if (not field_info.get('read_only') and
                isinstance(field, SlugRelatedField) and
                hasattr(field, 'queryset')):
            qset = field.queryset
            from django.shortcuts import reverse
            field_info['list_url'] = reverse('%s-list' % qset.model._meta.model_name)
            field_info['slug_field'] = field.slug_field
        return field_info
