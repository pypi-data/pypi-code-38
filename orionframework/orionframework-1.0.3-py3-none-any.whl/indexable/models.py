from django.db.models import QuerySet, Manager, Model, IntegerField
from django_extensions.db.models import ActivatorModelManager, ActivatorQuerySet


class IndexedQuerySet(QuerySet):

    def indexed(self):
        return self.order_by("index")


class IndexedModelManager(Manager):

    def get_queryset(self):
        return IndexedQuerySet(self.model, using=self._db)

    def reorder(self, keys):
        """
        Re-order all the items mapped the given indexed map of keys

        @param Class the class type we are re-ordering

        @param keys the map holding the pk -> index values
        """

        fields = ["index"]

        if isinstance(keys, (list, tuple)):

            index = 0

            for key in keys:
                model = self.model(id=key)
                model.index = index
                model.save(update_fields=fields)

                index += 1

        elif isinstance(keys, dict):

            for key in keys.keys():
                model = self.model(id=key)
                model.index = keys.get(key)
                model.save(update_fields=fields)

        else:
            raise Exception(
                "Expecting list/tuple of identifiers or dictionary of {id=index} but instead got: " + keys.__class__.name)


class IndexedModel(Model):
    index = IntegerField(null=True, blank=True, db_index=True)
    objects = IndexedModelManager()

    class Meta:
        abstract = True


# Utilities

class ActivatorIndexedQuerySet(ActivatorQuerySet, IndexedQuerySet):
    pass


class ActivatorIndexedModelManager(ActivatorModelManager, IndexedModelManager):

    def get_queryset(self):
        return ActivatorIndexedQuerySet(self.model, using=self._db)
