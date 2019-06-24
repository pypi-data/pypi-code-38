#    Boilerplate commons for django based web api application.
#    Copyright (C) 2017 Logicify
#    The MIT License (MIT)
#    
#    Permission is hereby granted, free of charge, to any person obtaining
#    a copy of this software and associated documentation files
#    (the "Software"), to deal in the Software without restriction,
#    including without limitation the rights to use, copy, modify, merge,
#    publish, distribute, sublicense, and/or sell copies of the Software,
#    and to permit persons to whom the Software is furnished to do so,
#    subject to the following conditions:
#    
#    The above copyright notice and this permission notice shall be
#    included in all copies or substantial portions of the Software.
#    
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#    TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from collections import Iterable
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty, Field
from rest_framework.serializers import Serializer


class BaseDto(Serializer):
    def to_dict(self):
        if not hasattr(self, '_data'):
            return self.initial_data
        else:
            return self.data

    def __init__(self, data=empty, **kwargs):
        self.initial_data = {}
        super(BaseDto, self).__init__(None, data, **kwargs)

    def __setattr__(self, key, value):
        if key in self.get_declared_fields():
            self.initial_data[key] = value
        else:
            super().__setattr__(key, value)

    def __getattr__(self, key):
        if key in self.get_declared_fields():
            return self.initial_data.get(key)
        else:
            if key in dir(super(BaseDto, self)):
                return getattr(super(), key)
            else:
                raise AttributeError("Object {} doesn't have attribute {}".format(self.__class__.__name__, key))

    @classmethod
    def from_dict(cls, dictionary=empty):
        instance = cls(dictionary)
        return instance

    @classmethod
    def get_declared_fields(cls):
        if hasattr(cls, '_declared_fields'):
            return getattr(cls, '_declared_fields')
        else:
            return []


class ApiResponseServiceSection(BaseDto):
    def __init__(self):
        self.error_code = 0
        self.error_message = None
        self.validation_errors = []
        self.api_version = settings.API_VERSION

    def is_successful(self):
        return self.error_code == 0

    def to_dict(self):
        return {
            "error_code": self.error_code,
            "node_id": settings.HOSTNAME,
            "error_message": self.error_message,
            "validation_errors": self.validation_errors,
            "successful": self.is_successful(),
            "api_version": self.api_version
        }


class ApiResponseDto(BaseDto):
    def __init__(self, payload=None):
        self.payload = payload
        self.service = ApiResponseServiceSection()

    def to_dict(self):
        serialized_payload = self.payload
        if isinstance(self.payload, BaseDto):
            serialized_payload = self.payload.to_representation(self.payload)
        elif isinstance(self.payload, Iterable):
            serialized_payload = list([(p.to_representation(p) if isinstance(p, BaseDto) else p) for p in self.payload])
        return {
            "payload": serialized_payload,
            "service": self.service.to_dict()
        }


class RelatedDtoField(Field):
    def __init__(self, dto_class, required: bool = None, default=empty, initial=empty) -> None:
        super().__init__(read_only=False, write_only=False, source=None, required=required, default=default,
                         initial=initial,
                         label=None, help_text=None, style=None, error_messages=None, validators=None, allow_null=False)
        self.dto_class = dto_class

    def to_representation(self, instance: BaseDto):
        if isinstance(instance, BaseDto):
            return instance.to_dict()
        elif isinstance(instance, dict):
            return instance
        else:
            raise ValueError("Unexpected value passed to to_representation method. " + str(instance))

    def to_internal_value(self, data: dict):
        dto = self.dto_class.from_dict(data)
        dto.is_valid()
        return dto

    def run_validators(self, value):
        if not value.is_valid():
            raise ValidationError(value.errors)


class PaginationOptions(object):
    """ Pagination options class, has offset and limit parameters."""

    def __init__(self, offset: int = 0, limit: int = 50) -> None:
        """ Return pagination options object with limit and offset.
        :param offset: Pagination offset
        :type offset: int
        :param limit: Pagination limit
        :type limit: int
        :rtype: PaginationOptions
        """
        self.offset = offset
        self.limit = limit
