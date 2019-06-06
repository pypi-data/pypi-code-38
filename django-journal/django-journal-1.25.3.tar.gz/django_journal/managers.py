from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.db.models import Q, Manager


class CachedQuerySet(QuerySet):
    def get_cached(self, **kwargs):
        instance, created = self.get_or_create(**kwargs)
        return instance


CachedManager = Manager.from_queryset(CachedQuerySet)


class TagManager(CachedManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class TemplateManager(CachedManager):
    def get_by_natural_key(self, content):
        return self.get(content=content)


class JournalQuerySet(QuerySet):
    def for_object(self, obj, tag=None):
        '''Return Journal records linked to this object.'''
        content_type = ContentType.objects.get_for_model(obj)
        if tag is None:
            return self.filter(objectdata__content_type=content_type,
                    objectdata__object_id=obj.pk)
        else:
            return self.filter(
                    objectdata__tag__name=tag,
                    objectdata__content_type=content_type,
                    objectdata__object_id=obj.pk)

    def for_objects(self, objects):
        '''Return journal records linked to any of this objects.

           All objects must have the same model.
        '''
        if not objects:
            return self.none()
        content_types = [ ContentType.objects.get_for_model(obj)
                for obj in objects ]
        if len(set(content_types)) != 1:
            raise ValueError('objects must have of the same content type')
        pks = [ obj.pk for obj in objects ]
        return self.filter(
                objectdata__content_type=content_types[0],
                objectdata__object_id__in=pks)

    def for_tag(self, tag):
        '''Returns Journal records linked to this tag by their own tag or
           the tag on their data records.
        '''
        from . import models

        if not isinstance(tag, models.Tag):
            try:
                tag = models.Tag.objects.get_cached(name=tag)
            except models.Tag.DoesNotExist:
                return self.none()
        # always remember: multiple join (OR in WHERE) produces duplicate
        # lines ! Use .distinct() for safety.
        return self.filter(Q(tag=tag)|
                Q(objectdata__tag=tag)|
                Q(stringdata__tag=tag)) \
                .distinct()


class JournalManager(Manager.from_queryset(JournalQuerySet)):
    def get_query_set(self):
        return super(JournalManager, self).get_query_set() \
               .prefetch_related('objectdata_set__content_type',
                       'stringdata_set', 'objectdata_set__tag',
                       'stringdata_set__tag', 'objectdata_set__content_object',
                       'tag', 'template') \
               .select_related('tag', 'template')
