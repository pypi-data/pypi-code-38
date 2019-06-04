import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from perestroika.context import Context


class Serializer:
    def serialize(self, context):
        raise NotImplementedError()

    def clean_item(self, item, project):
        to_drop = [
            k
            for k in item.keys()
            if k not in project
        ]

        for k in to_drop:
            del item[k]

    def apply_project(self, context: Context):
        if context.project:
            for item in context.items:
                self.clean_item(item, context.project)

    def get_data(self, context: Context):
        _data = {}

        self.apply_project(context)

        for name in [
            'items',

            'order', 'filter', 'exclude',

            'project',
            'status_code',

            'limit', 'skip',

            'total', 'created', 'updated', 'deleted',
        ]:
            value = getattr(context, name)
            if value:
                _data[name] = getattr(context, name)

        return _data


class DjangoSerializer(Serializer):
    @staticmethod
    def get_encoder():
        return DjangoJSONEncoder

    def serialize(self, context: Context):
        _data = self.get_data(context)

        return JsonResponse(_data, status=context.status_code, encoder=self.get_encoder())


class JSONSerializer(Serializer):
    @staticmethod
    def get_encoder():
        return json.JSONEncoder

    def serialize(self, context: Context):
        _data = self.get_data(context)

        return json.dumps(_data, cls=self.get_encoder())
