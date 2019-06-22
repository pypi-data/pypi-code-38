from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from mint import utils
from mint import exceptions
import collections


class BaseMixin(object):
    def _filter(self, queryset):
        return queryset

    def _slice(self, queryset):
        if self.limit and self.offset:
            return queryset[self.offset:self.offset+self.limit]
        elif self.limit:
            return queryset[:self.limit]
        elif self.offset:
            return queryset[self.offset]
        return queryset

    def _pre_run(self):
        pass

    def _post_run(self, model):
        pass

    def _pre_serialize(self):
        pass

    def _post_serialize(self):
        pass

    def _pre_delete(self, model):
        pass

    def _post_delete(self):
        pass

    def _pre_create(self, model):
        pass

    def _post_create(self, model):
        pass

    def _pre_update(self, model):
        pass

    def _post_update(self, model):
        pass

    def _pre_save(self, model):
        pass

    def _post_save(self, model):
        pass

    def _can_get(self):
        return True

    def _can_list(self):
        return True

    def _can_update(self):
        return True

    def _can_delete(self):
        return False

    def _can_create(self):
        return True

    def _iterate_and_serialize(self, model):
        out = []
        for m in model:
            out.append(self._serialize(m))
        return out

    def _get_serializer_fields(self):
        return []

    def _serialize(self, model):
        self._pre_serialize()
        out = self.serializer_instance.pack(model)
        self._post_serialize()
        return out

    def _get_name(self):
        return self.__class__.__name__

    def _format_plural(self, out, name=None, extra=None):
        if extra is None:
            extra = {}
        if not name:
            name = utils.camel_to_underscore(self._get_name())
        if name[-1:] != "s":
            name = "%ss" % name
        extra[name] = out
        ret = dict(extra, **self._get_return_metadata(self.model))
        return ret

    def _format_singular(self, out, name=None, extra=None):
        if extra is None:
            extra = {}
        if not name:
            name = utils.camel_to_underscore(self._get_name())
        if name[-1:] == "s":
            name = name[:-1]
        extra[name] = out
        ret = dict(extra, **self._get_return_metadata(self.model))
        return ret

    def _return(self, model):
        if isinstance(model, collections.Iterable):
            return self._iterate_and_serialize(model)
        return self._serialize(model)

    def _get_return_metadata(self, model):
        if isinstance(model, QuerySet):
            count = model.count()
        else:
            count = 1
        return {
            'count': count,
            'limit': self.limit,
            'offset': self.offset
        }


class ListMixin(BaseMixin):
    def list(self):
        self._pre_run()
        if not self._can_list():
            raise exceptions.HttpUnauthorized("You cannot list this object")
        self.model = self._slice(self._filter(self.model))
        self._post_run(self.model)
        return self._format_plural(self._return(self.model))

    def create(self):
        self._pre_run()
        if not self._can_create():
            raise exceptions.HttpUnauthorized("You cannot delete this object")
        m = self.original_model()
        for field in self.serializer_instance.required_create_fields:
            if field not in self.args.keys():
                raise exceptions.ParameterError("Parameter '%s' is required." % field)
        for key, value in self.args.items():
            if hasattr(m, key) and key in self.serializer_instance.can_create_fields:
                my_type = m._meta.get_field(key).get_internal_type()
                if my_type in ('DateTimeField', 'DateField'):
                    if value:
                        value = utils.datetime_from_string(value)
                elif hasattr(self.model, 'get_%s_display' % key):
                    values = dict((key, value) for (value, key) in self.model._meta.get_field(key).choices)
                    if value not in values:
                        raise exceptions.ParameterError("Invalid value for '%s' parameter.")
                    value = values[value]
                setattr(m, key, value)
        self._pre_create(m)
        self._pre_save(m)
        m.save()
        self._post_save(m)
        self._post_create(m)
        self._post_run(m)
        return self._format_singular(self._return(m))

    def _put_root(self):
        raise exceptions.HttpNotAllowed("Cannot PUT on root context")

    def _delete_root(self):
        raise exceptions.HttpNotAllowed("Cannot DELETE on root context")

    def _list_methods(self):
        return {
            'GET': self.list,
            'POST': self.create,
            'PUT': self._put_root,
            'DELETE': self._delete_root,
        }


class DetailMixin(BaseMixin):
    def get(self):
        self._pre_run()
        if not self._can_get():
            raise exceptions.HttpUnauthorized("You cannot get this object")
        self._post_run(self.model)
        return self._format_singular(self._return(self.model))

    def _post_by_id(self):
        raise exceptions.HttpNotAllowed("Cannot POST by ID")

    def update(self):
        self._pre_run()
        if not self._can_update():
            raise exceptions.HttpUnauthorized("You cannot update this object")
        self._pre_update(self.model)
        for field in self.serializer_instance.required_update_fields:
            if field not in self.args.keys():
                raise exceptions.ParameterError("Parameter '%s' is required." % field)
        for key, value in self.args.items():
            if hasattr(self.model, key) and key in self.serializer_instance.can_update_fields:
                my_type = self.model._meta.get_field(key).get_internal_type()
                if my_type in ('DateTimeField', 'DateField'):
                    value = utils.datetime_from_string(value)
                elif hasattr(self.model, 'get_%s_display' % key):
                    values = dict((key, value) for (value, key) in self.model._meta.get_field(key).choices)
                    if value not in values:
                        raise exceptions.ParameterError("Invalid value for '%s' parameter.")
                    value = values[value]
                setattr(self.model, key, value)
        self._pre_save(self.model)
        self.model.save()
        self._post_save(self.model)
        self._post_update(self.model)
        self._post_run(self.model)
        return self._format_singular(self._return(self.model))

    def delete(self):
        self._pre_run()
        if not self._can_delete():
            raise exceptions.HttpUnauthorized("You cannot delete this object")
        self._pre_delete(self.model)
        self.model.delete()
        self._post_delete()
        self._post_run(self.model)
        return True

    def _detail_methods(self):
        return {
            'GET': self.get,
            'POST': self._post_by_id,
            'PUT': self.update,
            'DELETE': self.delete,
        }


class FieldMixin(object):
    def has_field(self, name):
        if 'fields' not in self.args:
            return False
        fields = self.args['fields'].split(",")
        return name in fields
