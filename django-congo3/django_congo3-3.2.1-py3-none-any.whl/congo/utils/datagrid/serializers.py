# -*- coding: utf-8 -*-
from django.db import models
from rest_framework import serializers


class CellSerializer(serializers.Serializer):
    column_id = serializers.ReadOnlyField(source = 'column.id')
    data = serializers.ReadOnlyField()
    raw_data = serializers.SerializerMethodField()
    as_html = serializers.ReadOnlyField(source = 'column.as_html')
    is_hidden = serializers.ReadOnlyField(source = 'column.hidden')

    def get_raw_data(self, obj):
        if isinstance(obj.raw_data, models.Model):
            return obj.raw_data.id
        return obj.raw_data

class RowSerializer(serializers.Serializer):
    obj_id = serializers.IntegerField(source = 'obj.id', read_only = True)
    cells = serializers.SerializerMethodField()
    extra_params = serializers.SerializerMethodField()

    def get_cells(self, obj):
        return [CellSerializer(c).data for c in obj.cells]

    def get_extra_params(self, obj):
        return obj.extra_params

class ColumnSerializer(serializers.Serializer):
    column_id = serializers.ReadOnlyField(source = 'id')
    label = serializers.ReadOnlyField()
    param_name = serializers.ReadOnlyField()
    is_sortable = serializers.BooleanField(read_only = True)
    is_hidden = serializers.BooleanField(read_only = True)
    is_visible = serializers.NullBooleanField(read_only = True)
    sort_priority = serializers.IntegerField(read_only = True)
    sort_dir = serializers.IntegerField(read_only = True)
    header_css_class = serializers.ReadOnlyField()
    cell_css_class = serializers.ReadOnlyField()
    sort_cols = serializers.ReadOnlyField(source = 'get_sort_cols')
    unsort_cols = serializers.ReadOnlyField(source = 'get_unsort_cols')


class DataGridSerializer(serializers.Serializer):
    grid_id = serializers.ReadOnlyField(source = 'id')
    columns = serializers.SerializerMethodField()
    column_map = serializers.SerializerMethodField()
    rows = serializers.SerializerMethodField()
    paginator = serializers.ReadOnlyField(source = 'get_paginator')
    # params = serializers.ReadOnlyField()
    sort = serializers.ReadOnlyField(source = 'get_sort')
    init_filters = serializers.ReadOnlyField(source = 'get_filters') # @md przy zmianie nazwy tego atrybutu posypie się wyświetlanie filtrow na gridzie

    def get_columns(self, obj):
        return [ColumnSerializer(c).data for c in obj.columns]

    def get_column_map(self, obj):
        return  dict([(c.id, index) for index, c in enumerate(obj.columns)])

    def get_rows(self, obj):
        return [RowSerializer(r).data for r in obj.rows]
