from collections import OrderedDict, Mapping
from typing import Any
from urllib import parse

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.urlresolvers import get_resolver, resolve, get_script_prefix, Resolver404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.encoding import uri_to_iri
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField, empty
from rest_framework.fields import get_error_detail, set_value
from rest_framework.relations import HyperlinkedRelatedField, ManyRelatedField, MANY_RELATION_KWARGS, Hyperlink
from rest_framework.serializers import HyperlinkedModelSerializer, ListSerializer, ModelSerializer
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta
from rest_framework.utils.field_mapping import get_nested_relation_kwargs
from rest_framework.utils.serializer_helpers import ReturnDict

from djangoldp.fields import LDPUrlField, IdURLField
from djangoldp.models import Model


class LDListMixin:
    child_attr = 'child'

    def to_internal_value(self, data):
        try:
            data = data['ldp:contains']
        except (TypeError, KeyError):
            pass
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, str) and data.startswith("http"):
            data = [{'@id': data}]

        return [getattr(self, self.child_attr).to_internal_value(item) for item in data]

    def to_representation(self, value):
        return {'@id': self.id,
                '@type': 'ldp:Container',
                'ldp:contains': super().to_representation(value),
                'permissions': Model.get_permissions(value.model, self.context['request'].user, ['view', 'add'])
                }

    def get_attribute(self, instance):
        parent_id_field = self.parent.fields[self.parent.url_field_name]
        context = self.parent.context
        parent_id = parent_id_field.get_url(instance, parent_id_field.view_name, context['request'], context['format'])
        self.id = parent_id + self.field_name + "/"
        return super().get_attribute(instance)

    def get_value(self, dictionary):
        try:
            object_list = dictionary['@graph']

            if self.parent.instance is None:
                obj = next(filter(
                    lambda o: not hasattr(o, self.parent.url_field_name) or "./" in o[self.parent.url_field_name],
                    object_list))
            else:
                container_id = Model.container_id(self.parent.instance)
                obj = next(filter(lambda o: container_id.lstrip('/') in o[self.parent.url_field_name], object_list))
            list = super().get_value(obj)
            try:
                list = next(
                    filter(lambda o: list[self.parent.url_field_name] == o[self.parent.url_field_name], object_list))
            except (KeyError, TypeError, StopIteration):
                pass

            try:
                list = list['ldp:contains']
            except (KeyError, TypeError):
                pass

            if list is empty:
                return []

            if isinstance(list, dict):
                list = [list]

            ret = []
            for item in list:
                full_item = None
                try:
                    full_item = next(filter(
                        lambda o: self.parent.url_field_name in o and item[self.parent.url_field_name] == o[
                            self.parent.url_field_name], object_list))
                except StopIteration:
                    pass
                if full_item is None:
                    ret.append(item)
                else:
                    ret.append(full_item)

            return ret
        except KeyError:
            obj = super().get_value(dictionary)
            if isinstance(obj, dict) and self.parent.url_field_name in obj:
                resource_id = obj[self.parent.url_field_name]
                if isinstance(resource_id, str) and resource_id.startswith("_:"):
                    object_list = self.root.initial_data['@graph']
                    obj = [next(filter(lambda o: resource_id in o[self.parent.url_field_name], object_list))]

            return obj


class ContainerSerializer(LDListMixin, ListSerializer):
    id = ''

    @property
    def data(self):
        return ReturnDict(super(ListSerializer, self).data, serializer=self)

    def create(self, validated_data):
        return super().create(validated_data)

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data[self.parent.url_field_name])
        except (KeyError, TypeError):
            return super().to_internal_value(data)


class ManyJsonLdRelatedField(LDListMixin, ManyRelatedField):
    child_attr = 'child_relation'
    url_field_name = "@id"



class JsonLdField(HyperlinkedRelatedField):
    def __init__(self, view_name=None, **kwargs):
        super().__init__(view_name, **kwargs)
        self.get_lookup_args()

    def get_lookup_args(self):
        try:
            lookup_field = get_resolver().reverse_dict[self.view_name][0][0][1][0]
            self.lookup_field = lookup_field
            self.lookup_url_kwarg = lookup_field
        except MultiValueDictKeyError:
            pass

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def get_value(self, dictionary):
        return super().get_value(dictionary)


class JsonLdRelatedField(JsonLdField):
    def to_representation(self, value):
        try:
            return {'@id': super().to_representation(value)}
        except ImproperlyConfigured:
            return value.pk

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data[self.parent.url_field_name])
        except (KeyError, TypeError):
            return super().to_internal_value(data)

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyJsonLdRelatedField(**list_kwargs)


class JsonLdIdentityField(JsonLdField):
    def __init__(self, view_name=None, **kwargs):
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super().__init__(view_name, **kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data[self.parent.url_field_name])
        except KeyError:
            return super().to_internal_value(data)

    def get_value(self, dictionary):
        return super().get_value(dictionary)

    def to_representation(self, value: Any) -> Any:
        try:
            return Hyperlink(value.webid(), value)
        except AttributeError:
            return super().to_representation(value)


class LDPSerializer(HyperlinkedModelSerializer):
    url_field_name = "@id"
    serializer_related_field = JsonLdRelatedField
    serializer_url_field = JsonLdIdentityField
    ModelSerializer.serializer_field_mapping[LDPUrlField] = IdURLField

    @property
    def data(self):
        return super().data

    def get_default_field_names(self, declared_fields, model_info):
        try:
            fields = list(self.Meta.model._meta.serializer_fields)
        except AttributeError:
            fields = super().get_default_field_names(declared_fields, model_info)
        if 'request' in self._context and not self._context['request']._request.method == 'GET':
            try:
                fields.remove(self.Meta.model._meta.auto_author)
            except ValueError:
                pass
            except AttributeError:
                pass
        return fields + list(getattr(self.Meta, 'extra_fields', []))

    def to_representation(self, obj):
        data = super().to_representation(obj)

        rdf_type = Model.get_meta(obj, 'rdf_type', None)
        rdf_context = Model.get_meta(obj, 'rdf_context', None)
        if rdf_type is not None:
            data['@type'] = rdf_type
        if rdf_context is not None:
            data['@context'] = rdf_context
        data['permissions'] = Model.get_permissions(obj, self.context['request'].user,
                                                    ['view', 'change', 'control', 'delete'])

        return data

    def build_field(self, field_name, info, model_class, nested_depth):
        nested_depth = self.compute_depth(nested_depth, model_class)

        return super().build_field(field_name, info, model_class, nested_depth)

    def build_standard_field(self, field_name, model_field):
        class JSonLDStandardField:
            parent_view_name = None

            def __init__(self, **kwargs):
                self.parent_view_name = kwargs.pop('parent_view_name')
                super().__init__(**kwargs)

            def get_value(self, dictionary):
                try:
                    object_list = dictionary["@graph"]
                    if self.parent.instance is None:
                        obj = next(filter(
                            lambda o: not hasattr(o, self.parent.url_field_name) or "./" in o[self.url_field_name],
                            object_list))
                        return super().get_value(obj)
                    else:
                        resource_id = Model.resource_id(self.parent.instance)
                        obj = next(filter(lambda o: resource_id.lstrip('/') in o[self.parent.url_field_name], object_list))
                        return super().get_value(obj)
                except KeyError:
                    return super().get_value(dictionary)

        field_class, field_kwargs = super().build_standard_field(field_name, model_field)
        field_kwargs['parent_view_name'] = '{}-list'.format(model_field.model._meta.object_name.lower())
        return type(field_class.__name__ + 'Valued', (JSonLDStandardField, field_class), {}), field_kwargs

    def build_nested_field(self, field_name, relation_info, nested_depth):
        nested_depth = self.compute_depth(nested_depth, self.Meta.model)

        class NestedLDPSerializer(self.__class__):

            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                try:
                    fields = ['@id'] + list(model._meta.serializer_fields)
                except AttributeError:
                    fields = '__all__'

            def to_internal_value(self, data):
                if self.url_field_name in data:
                    if not isinstance(data, Mapping):
                        message = self.error_messages['invalid'].format(
                            datatype=type(data).__name__
                        )
                        raise ValidationError({
                            api_settings.NON_FIELD_ERRORS_KEY: [message]
                        }, code='invalid')

                    ret = OrderedDict()
                    errors = OrderedDict()
                    fields = list(filter(lambda x: x.field_name in data, self._writable_fields))

                    for field in fields:
                        validate_method = getattr(self, 'validate_' + field.field_name, None)
                        primitive_value = field.get_value(data)
                        try:
                            validated_value = field.run_validation(primitive_value)
                            if validate_method is not None:
                                validated_value = validate_method(validated_value)
                        except ValidationError as exc:
                            errors[field.field_name] = exc.detail
                        except DjangoValidationError as exc:
                            errors[field.field_name] = get_error_detail(exc)
                        except SkipField:
                            pass
                        else:
                            set_value(ret, field.source_attrs, validated_value)

                    if errors:
                        raise ValidationError(errors)

                    uri = data[self.url_field_name]
                    http_prefix = uri.startswith(('http:', 'https:'))

                    if http_prefix:
                        uri = parse.urlparse(uri).path
                        prefix = get_script_prefix()
                        if uri.startswith(prefix):
                            uri = '/' + uri[len(prefix):]

                    try:
                        match = resolve(uri_to_iri(uri))
                        slug_field = Model.slug_field(self.__class__.Meta.model)
                        ret[slug_field] = match.kwargs[slug_field]
                    except Resolver404:
                        pass

                    return ret
                else:
                    return super().to_internal_value(data)

        kwargs = get_nested_relation_kwargs(relation_info)
        kwargs['read_only'] = False
        kwargs['required'] = False
        return NestedLDPSerializer, kwargs

    @classmethod
    def compute_depth(cls, depth, model_class, name='depth'):
        try:
            model_depth = getattr(model_class._meta, 'depth', getattr(model_class.Meta, 'depth', 10))
            depth = min(depth, int(model_depth))
        except AttributeError:
            depth = min(depth, int(getattr(model_class._meta, 'depth', 1)))

        return depth

    @classmethod
    def many_init(cls, *args, **kwargs):
        kwargs['child'] = cls(**kwargs)
        try:
            cls.Meta.depth = cls.compute_depth(kwargs['context']['view'].many_depth, cls.Meta.model, 'many_depth')
        except KeyError:
            pass
        return ContainerSerializer(*args, **kwargs)

    def get_value(self, dictionary):
        try:
            object_list = dictionary["@graph"]
            if self.parent.instance is None:
                obj = next(filter(
                    lambda o: not hasattr(o, self.parent.url_field_name) or "./" in o[self.url_field_name],
                    object_list))
            else:
                container_id = Model.container_id(self.parent.instance)
                obj = next(filter(lambda o: container_id.lstrip('/') in o[self.url_field_name], object_list))
            item = super().get_value(obj)
            full_item = None
            if item is empty:
                return empty
            try:
                full_item = next(filter(lambda o: self.url_field_name in o and (item[self.url_field_name] == o[self.url_field_name]), object_list))
            except StopIteration:
                pass
            if full_item is None:
                return item
            else:
                return full_item

        except KeyError:
            return super().get_value(dictionary)

    def create(self, validated_data):
        instance = self.internal_create(validated_data, model=self.Meta.model)

        self.attach_related_object(instance, validated_data)

        return instance

    def attach_related_object(self, instance, validated_data):
        model_class = self.Meta.model

        info = model_meta.get_field_info(model_class)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and relation_info.reverse and not (
                    field_name in validated_data) and not field_name is None:
                rel = getattr(instance._meta.model, field_name).rel
                if rel.name in validated_data:
                    related = validated_data[rel.name]
                    getattr(instance, field_name).add(related)

    def internal_create(self, validated_data, model):

        nested_fk_fields_name = list(filter(lambda key: isinstance(validated_data[key], dict), validated_data))
        for field_name in nested_fk_fields_name:
            field_dict = validated_data[field_name]
            field_model = getattr(model, field_name).field.rel.model
            slug_field = Model.slug_field(field_model)
            if slug_field in field_dict:
                kwargs = {slug_field: field_dict[slug_field]}
                sub_inst = field_model.objects.get(**kwargs)
            else:
                sub_inst = self.internal_create(field_dict, field_model )
            validated_data[field_name] = sub_inst

        nested_fields = []
        nested_list_fields_name = list(filter(lambda key: isinstance(validated_data[key], list), validated_data))
        for field_name in nested_list_fields_name:
            nested_fields.append((field_name, validated_data.pop(field_name)))

        instance = model.objects.create(**validated_data)

        self.save_or_update_nested_list(instance, nested_fields)

        return instance

    def update(self, instance, validated_data):
        nested_fields = []
        nested_fields_name = list(filter(lambda key: isinstance(validated_data[key], list), validated_data))
        for field_name in nested_fields_name:
            nested_fields.append((field_name, validated_data.pop(field_name)))

        for attr, value in validated_data.items():
            if isinstance(value, dict):
                value = self.update_dict_value(attr, instance, value)
            setattr(instance, attr, value)

        instance.save()

        self.save_or_update_nested_list(instance, nested_fields)

        return instance

    def update_dict_value(self, attr, instance, value):
        info = model_meta.get_field_info(instance)
        slug_field = Model.slug_field(instance)
        relation_info = info.relations.get(attr)
        if slug_field in value:
            value = self.update_dict_value_when_id_is_provided(attr, instance, relation_info, slug_field, value)
        else:
            value = self.update_dict_value_without_slug_field(attr, instance, relation_info, value)
        return value

    def update_dict_value_without_slug_field(self, attr, instance, relation_info, value):
        if relation_info.to_many:
            value = self.internal_create(validated_data=value, model=relation_info.related_model)
        else:
            value[instance._meta.fields_map[attr].remote_field.name] = instance
            oldObj = getattr(instance, attr, None)
            if oldObj is None:
                value = self.internal_create(validated_data=value, model=relation_info.related_model)
            else:
                value = self.update(instance=oldObj, validated_data=value)
        return value

    def update_dict_value_when_id_is_provided(self, attr, instance, relation_info, slug_field, value):
        kwargs = {slug_field: value[slug_field]}
        if relation_info.to_many:
            manager = getattr(instance, attr)
            oldObj = manager._meta.model.objects.get(**kwargs)
        else:
            oldObj = getattr(instance, attr)

        value = self.update(instance=oldObj, validated_data=value)
        return value

    def save_or_update_nested_list(self, instance, nested_fields):
        for (field_name, data) in nested_fields:
            manager = getattr(instance, field_name)
            slug_field = Model.slug_field(instance)
            try:
                item_pk_to_keep = list(map(lambda e: e[slug_field], filter(lambda x: slug_field in x, data)))
            except TypeError:
                item_pk_to_keep = list(map(lambda e: getattr(e, slug_field), filter(lambda x: hasattr(x, slug_field), data)))

            for item in list(manager.all()):
                if not str(getattr(item, slug_field)) in item_pk_to_keep:
                    if getattr(manager, 'through', None) is None:
                        item.delete()
                    else:
                        manager.remove(item)

            for item in data:
                if not isinstance(item, dict):
                    item.save()
                    saved_item = item
                elif slug_field in item:
                    kwargs = {slug_field: item[slug_field]}
                    old_obj = manager.model.objects.get(**kwargs)
                    saved_item = self.update(instance=old_obj, validated_data=item)
                else:
                    rel = getattr(instance._meta.model, field_name).rel
                    try:
                        if rel.related_model == manager.model:
                            reverse_id = rel.remote_field.attname
                            item[reverse_id] = instance.pk
                    except AttributeError:
                        pass
                    saved_item = self.internal_create(validated_data=item, model=manager.model)

                if getattr(manager, 'through', None) is not None and manager.through._meta.auto_created:
                    manager.add(saved_item)
