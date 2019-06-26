from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.db import models
from django.db.models.base import ModelBase
from django.urls import get_resolver
from django.utils.decorators import classonlymethod
from guardian.shortcuts import get_perms

User._meta.rdf_type = "foaf:user"


class Model(models.Model):

    @classmethod
    def get_view_set(cls):
        view_set = getattr(cls._meta, 'view_set', getattr(cls.Meta, 'view_set', None))
        if view_set is None:
            from djangoldp.views import LDPViewSet
            view_set = LDPViewSet
        return view_set

    @classmethod
    def get_container_path(cls):
        path = getattr(cls._meta, 'container_path', getattr(cls.Meta, 'container_path', None))
        if path is None:
            path = "{}s".format(cls._meta.object_name.lower())

        return path

    def get_absolute_url(self):
        return Model.resource_id(self)

    def get_container_id(self):
        return Model.container_id(self)

    @classonlymethod
    def resource_id(cls, instance):
        r_id = "{}{}".format(cls.container_id(instance), getattr(instance, cls.slug_field(instance)))
        return cls.__clean_path(r_id)

    @classonlymethod
    def slug_field(cls, instance_or_model):
        if isinstance(instance_or_model, ModelBase):
            object_name = instance_or_model.__name__.lower()
        else:
            object_name = instance_or_model._meta.object_name.lower()
        view_name = '{}-detail'.format(object_name)
        slug_field = '/{}'.format(get_resolver().reverse_dict[view_name][0][0][1][0])
        if slug_field.startswith('/'):
            slug_field = slug_field[1:]
        return slug_field

    @classonlymethod
    def container_id(cls, instance):
        if isinstance(instance, cls):
            path = instance.get_container_path()
        else:
            view_name = '{}-list'.format(instance._meta.object_name.lower())
            path = get_resolver().reverse(view_name)

        path = cls.__clean_path(path)

        return path

    class Meta:
        default_permissions = ('add', 'change', 'delete', 'view', 'control')
        abstract = True
        depth = 1
        many_depth = 0

    @classonlymethod
    def resolve_id(cls, id):
        id = cls.__clean_path(id)
        view, args, kwargs = get_resolver().resolve(id)
        return view.initkwargs['model'].objects.get(**kwargs)

    @classonlymethod
    def resolve_container(cls, path):
        path = cls.__clean_path(path)
        view, args, kwargs = get_resolver().resolve(path)
        return view.initkwargs['model']

    @classonlymethod
    def resolve(cls, path):
        container = cls.resolve_container(path)
        try:
            resolve_id = cls.resolve_id(path)
        except:
            resolve_id = None
        return container, resolve_id

    @classonlymethod
    def __clean_path(cls, path):
        if not path.startswith("/"):
            path = "/{}".format(path)
        if not path.endswith("/"):
            path = "{}/".format(path)
        return path

    @classonlymethod
    def get_permission_classes(cls, related_model, default_permissions_classes):
        return cls.get_meta(related_model, 'permission_classes', default_permissions_classes)

    @classonlymethod
    def get_meta(cls, model_class, meta_name, default=None):
        if hasattr(model_class, 'Meta'):
            meta = getattr(model_class.Meta, meta_name, default)
        else:
            meta = default
        return getattr(model_class._meta, meta_name, meta)

    @staticmethod
    def get_permissions(obj_or_model, user_or_group, filter):
        permissions = filter
        for permission_class in Model.get_permission_classes(obj_or_model, []):
            permissions = permission_class().filter_user_perms(user_or_group, obj_or_model, permissions)

        if not isinstance(user_or_group, AnonymousUser):
            permissions += get_perms(user_or_group, obj_or_model)
        return [{'mode': {'@type': name.split('_')[0]}} for name in permissions]


class LDPSource(models.Model):
    container = models.URLField()
    federation = models.CharField(max_length=255)

    class Meta:
        rdf_type = 'sib:source'
        ordering = ('federation',)
        permissions = (
            ('view_source', 'acl:Read'),
            ('control_source', 'acl:Control'),
        )

    def __str__(self):
        return "{}: {}".format(self.federation, self.container)
