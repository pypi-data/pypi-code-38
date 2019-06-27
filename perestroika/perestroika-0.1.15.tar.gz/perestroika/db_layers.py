from django.db.models import Q

from perestroika.context import Context
from perestroika.exceptions import BadRequest


class DbLayer:
    pass


class DjangoDbLayer(DbLayer):
    @classmethod
    def queryset_to_items(cls, context):
        return context.queryset.values()

    @classmethod
    def merge_filters(cls, context: Context):
        query = Q()

        if context.user_filter:
            query &= Q(**context.user_filter)

        if context.system_filter:
            query &= context.system_filter

        context.merged_filter = query

    @classmethod
    def merge_excludes(cls, context: Context):
        query = Q()

        if context.user_exclude:
            query &= Q(**context.user_exclude)

        if context.system_exclude:
            query &= context.system_exclude

        context.merged_exclude = query

    @classmethod
    def get(cls, context: Context, method):
        cls.merge_filters(context)
        cls.merge_excludes(context)

        context.queryset = context.queryset.filter(context.merged_filter)
        context.queryset = context.queryset.exclude(context.merged_exclude)

        if context.project:
            context.queryset = context.queryset.only(*context.project)

        context.items = cls.queryset_to_items(context)

        if method.count_total:
            context.total = context.queryset.count()

    @staticmethod
    def post(context: Context, method):
        if not context.items:
            raise BadRequest(message="Empty data for insert")

        items = [context.queryset.model(**data) for data in context.items]

        context.queryset.model.objects.bulk_create(items)
        context.created = len(items)

    @classmethod
    def put(cls, context: Context, method):
        if not context.items:
            raise BadRequest(message="Empty data for update")

        cls.merge_filters(context)
        cls.merge_excludes(context)

        context.queryset = context.queryset.filter(context.merged_filter)
        context.queryset = context.queryset.exclude(context.merged_exclude)

        updated = 0

        for item in context.items:
            updated += context.queryset.update(**item)

        context.updated = updated
