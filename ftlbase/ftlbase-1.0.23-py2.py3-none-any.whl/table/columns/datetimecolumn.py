#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from django.utils import timezone
from django.utils.html import escape

from table.utils import Accessor
from .base import Column


class DatetimeColumn(Column):

    # DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"
    DEFAULT_FORMAT = "%Y-%m-%d %H:%M"

    def __init__(self, field, header=None, format=None, **kwargs):
        self.format = format or DatetimeColumn.DEFAULT_FORMAT
        super(DatetimeColumn, self).__init__(field, header, **kwargs)

    def render(self, obj):
        obj_datetime = Accessor(self.field).resolve(obj)
        if isinstance(obj_datetime, datetime):
            text = timezone.localtime(obj_datetime).strftime(self.format)
        elif obj_datetime:
            text = obj_datetime.strftime(self.format)
        else:
            text = u''
        return escape(text)
