from django.conf import settings
from django.core import serializers
from mint import utils
import collections
try:
    from hashid_field import Hashid
except ImportError:
    Hashid = None


class Serializer(object):
    return_fields = ()

    can_update_fields = ()
    can_create_fields = ()

    required_update_fields = ()
    required_create_fields = ()

    transformers = {}

    default_transformers = {
        'DateTimeField': utils.string_from_datetime,
        'DateField': utils.string_from_datetime,
        'TimeField': utils.string_from_time,
        'DecimalField': float,
        'FileField': lambda value: "%s%s" % (settings.MEDIA_URL, value),
        'ManyToManyField': lambda value: []

    }

    def __init__(self, controller):
        self.controller = controller

    def pack(self, model):
        fields = serializers.serialize('python', (model, ))[0]['fields']
        out = {}
        out_fields = self.return_fields
        for name, value in fields.items():
            if name in out_fields:
                if hasattr(self, name):
                    relationship = getattr(self, name)
                    out[name] = relationship.serialize(self.controller, model)
                else:
                    my_type = model._meta.get_field(name).get_internal_type()
                    out[name] = self.transform_field(model, my_type, name, value)
                    if my_type in ['ForeignKey']:
                        key = "%s_id" % name
                        out[key] = value
                        del out[name]
        if 'id' in out_fields:
            if Hashid and isinstance(model.id, Hashid):
                out['id'] = str(model.id)
            else:
                out['id'] = model.id
        out['model'] = utils.camel_to_underscore(model.__class__.__name__)
        self.pre_return(model, out)
        return out

    def transform_field(self, model, type, name, value):
        transformers = dict(self.default_transformers, **self.transformers)
        if type in transformers:
            value = transformers[type](value)
        if hasattr(model, 'get_%s_display' % name):
            return getattr(model, 'get_%s_display' % name)()
        else:
            return value

    def pre_return(self, model, out):
        pass


class Relationship(object):
    def __init__(self, relationship_class, serializer_class, field_name, required_field=None, related_name=None):
        self.relationship_class = relationship_class
        self.serializer_class = serializer_class
        self.field_name = field_name
        self.required_field = required_field
        self.related_name = related_name

    def serialize(self, controller, model):
        instance = self.relationship_class(self, controller)
        return instance.serialize(model)


class ForeignKeyRelationship(Relationship):
    def __init__(self, serializer_class, field_name, required_field=None, related_name=None):
        super().__init__(ForeignKeySerializer, serializer_class, field_name, required_field, related_name)


class ManyToManyFieldRelationship(Relationship):
    def __init__(self, serializer_class, field_name, required_field=None, related_name=None):
        super().__init__(ManyToManyFieldSerializer, serializer_class, field_name, required_field, related_name)


class RelationshipSerializer(object):
    def __init__(self, manager, controller):
        self.manager = manager
        self.controller = controller
        self.serializer_instance = None

    def get_serializer(self):
        if not self.serializer_instance:
            self.serializer_instance = self.manager.serializer_class(self.controller)
        return self.serializer_instance

    def check_for_field(self):
        if self.manager.required_field:
            return self.controller.has_field(self.manager.required_field)
        return True

    def serialize(self, model):
        raise NotImplementedError("Must be implemented in extending class.")


class ForeignKeySerializer(RelationshipSerializer):
    def serialize(self, model):
        if not self.check_for_field():
            return None
        field = getattr(model, self.manager.field_name)
        if self.manager.related_name:
            field = getattr(field, self.manager.related_name)
        if field is not None:
            return self.get_serializer().pack(field)
        return field


class ManyToManyFieldSerializer(RelationshipSerializer):
    def serialize(self, model):
        out = []
        if not self.check_for_field():
            return out
        for model in getattr(model, self.manager.field_name).all():
            if self.manager.related_name:
                model = getattr(model, self.manager.related_name)
            out.append(self.get_serializer().pack(model))
        return out


def serialize(controller, serializer_class, model, related_name=None):
    if isinstance(model, collections.Iterable):
        out = []
        for item in model:
            if related_name:
                item = getattr(item, related_name)
            out.append(serializer_class(controller).pack(item))
        return out
    return serializer_class(controller).pack(model)
