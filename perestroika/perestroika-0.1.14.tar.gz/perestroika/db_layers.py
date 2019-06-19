from perestroika.context import Context
from perestroika.exceptions import BadRequest


class DbLayer:
    pass


class DjangoDbLayer(DbLayer):
    @classmethod
    def queryset_to_items(cls, context):
        return context.queryset.values()

    @classmethod
    def get(cls, context: Context, method):
        if context.filter:
            context.queryset = context.queryset.filter(**context.filter)

        if context.exclude:
            context.queryset = context.queryset.exclude(**context.exclude)

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

    @staticmethod
    def put(context: Context, method):
        if not context.items:
            raise BadRequest(message="Empty data for update")

        if context.filter:
            context.queryset = context.queryset.filter(**context.filter)

        if context.exclude:
            context.queryset = context.queryset.exclude(**context.exclude)

        updated = 0

        for item in context.items:
            updated += context.queryset.update(**item)

        context.updated = updated
