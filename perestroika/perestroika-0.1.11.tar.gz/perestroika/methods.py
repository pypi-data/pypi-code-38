import logging
from collections import Callable
from typing import List, Any, Optional

import attr

from perestroika.context import Context
from perestroika.db_layers import DbLayer, DjangoDbLayer
from perestroika.deserializers import Deserializer, DjangoDeserializer
from perestroika.exceptions import RestException, BadRequest, InternalServerError
from perestroika.serializers import Serializer, DjangoSerializer
from perestroika.validators import DenyAll

logger = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class Method:
    mode: str = 'django'

    query: Any = None
    queryset: Any = None
    db_layer: Optional[DbLayer] = None

    serializer: Optional[Serializer] = None
    deserializer: Optional[Deserializer] = None

    skip_query_db: bool = False
    count_total: bool = False

    input_validator: Callable = DenyAll
    output_validator: Callable = DenyAll

    pre_query_hooks: List[Callable] = attr.Factory(list)
    post_query_hooks: List[Callable] = attr.Factory(list)

    request_hooks: List[Callable] = attr.Factory(list)
    response_hooks: List[Callable] = attr.Factory(list)

    def __attrs_post_init__(self):
        need_fields = []

        if self.mode == 'django':
            need_fields = ['queryset']

            if not self.db_layer:
                self.db_layer = DjangoDbLayer()

            if not self.serializer:
                self.serializer = DjangoSerializer()

            if not self.deserializer:
                self.deserializer = DjangoDeserializer()

        for field in need_fields:
            if getattr(self, field) is None and not self.skip_query_db:
                raise ValueError(f"Empty `{field}` is allowed only for resources with `skip_query_db` == True")

    def __set_name__(self, owner, name):
        if not hasattr(owner, 'methods') or not owner.methods:
            setattr(owner, 'methods', {})

        owner.methods[self.__class__.__name__.lower()] = self

    def schema(self):
        return {
            "output_schema": repr(self.output_validator)
        }

    def query_db(self, context: Context):
        raise NotImplementedError()

    @staticmethod
    def validate(validator, context: Context, validation_exception_class=RestException):
        _errors = []
        items = []

        for item in context.items:
            try:
                item = validator(item)
                items.append(item)
            except Exception as e:
                _desc = {
                    "data": item,
                    "error": e
                }
                _errors.append(e)

        if _errors:
            raise validation_exception_class(message="Wrong data", errors=_errors)

        context.items = items

    def validate_input(self, context: Context):
        self.validate(self.input_validator, context, validation_exception_class=BadRequest)

    def validate_output(self, context: Context):
        self.validate(self.output_validator, context, validation_exception_class=InternalServerError)

    @staticmethod
    def apply_hooks(hooks, context: Context):
        for hook in hooks:
            hook(context)

    def apply_pre_query_hooks(self, context: Context):
        self.apply_hooks(self.pre_query_hooks, context)

    def apply_post_query_hooks(self, context: Context):
        self.apply_hooks(self.post_query_hooks, context)

    def set_default_success_code(self, context: Context):
        raise NotImplementedError()

    def apply_request_hooks(self, context: Context):
        self.apply_hooks(self.request_hooks, context)

    def apply_response_hooks(self, context: Context):
        self.apply_hooks(self.response_hooks, context)

    def handle(self, request, **kwargs):
        context = self.deserializer.deserialize(request, self, **kwargs)

        self.set_default_success_code(context)
        self.apply_request_hooks(context)
        self.validate_input(context)
        self.apply_pre_query_hooks(context)

        if not self.skip_query_db:
            self.query_db(context)

        self.apply_post_query_hooks(context)
        self.validate_output(context)
        self.apply_response_hooks(context)

        return self.serializer.serialize(context)


@attr.s(auto_attribs=True)
class CanFilterAndExclude(Method):
    filter_validator: Callable = DenyAll
    exclude_validator: Callable = DenyAll

    def set_default_success_code(self, context: Context):
        raise NotImplementedError()

    def query_db(self, context: Context):
        raise NotImplementedError()

    def schema(self):
        _schema = super().schema()
        _schema["filter_schema"] = repr(self.filter_validator)
        _schema["exclude_schema"] = repr(self.exclude_validator)
        return _schema


@attr.s(auto_attribs=True)
class NoBodyNoObjectsNoInput(CanFilterAndExclude):
    def set_default_success_code(self, context: Context):
        raise NotImplementedError()

    def validate_input(self, context: Context):
        """ Void validation because no input data"""
        pass

    def query_db(self, context: Context):
        raise NotImplementedError()


@attr.s(auto_attribs=True)
class Get(NoBodyNoObjectsNoInput):
    def query_db(self, context: Context):
        self.db_layer.get(context, self)

    def set_default_success_code(self, context: Context):
        context.status_code = 200


@attr.s(auto_attribs=True)
class Post(Method):
    input_validator: Callable = DenyAll

    def query_db(self, context: Context):
        self.db_layer.post(context, self)
        context.items = {}

    def schema(self):
        _schema = super().schema()
        _schema["input_schema"] = repr(self.input_validator)
        return _schema

    def set_default_success_code(self, context: Context):
        context.status_code = 201


@attr.s(auto_attribs=True)
class Put(CanFilterAndExclude):
    def query_db(self, context: Context):
        self.db_layer.put(context, self)
        context.items = {}

    input_validator: Callable = DenyAll

    def set_default_success_code(self, context: Context):
        context.status_code = 200

    def schema(self):
        _schema = super().schema()
        _schema["input_schema"] = repr(self.input_validator)
        return _schema


@attr.s(auto_attribs=True)
class Delete(NoBodyNoObjectsNoInput):
    def query_db(self, context: Context):
        raise NotImplementedError()

    def set_default_success_code(self, context: Context):
        context.status_code = 204


__all__ = [
    "Get",
    "Post",
    "Put",
    "Delete"
]
