from django.db.models import Model
from json import JSONEncoder
from typing import List
from datetime import datetime, date
from CTUtil.types import EnumJsonEncode


class DjangoSerializer(EnumJsonEncode):
    def default(self, obj: Model):
        if isinstance(obj, Model):
            file_list: List[str] = [
                f.name for f in obj._meta.get_fields()
                if f.concrete and (not f.is_relation or f.one_to_one or
                                   (f.many_to_one and f.related_model))
            ]
            data = {}
            for file in file_list:
                value = getattr(obj, file)
                if isinstance(value, datetime):
                    value = format(value, '%Y-%m-%d %H-%M')
                elif isinstance(value, date):
                    value = format(value, '%Y-%m-%d')
                else:
                    value = str(value)
                data[file] = value
            return data
        return super().default(obj)
