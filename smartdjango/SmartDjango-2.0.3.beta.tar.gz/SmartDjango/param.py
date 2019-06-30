import re
from typing import List

from django.db import models

from .error import BaseError
from .packing import Packing
from .model import SmartModel


class Param:
    class __NoDefault:
        pass

    class Classify:
        def dict(self, *args):
            if args:
                _dict = dict()
                for k in args:
                    _dict[k] = self._dict.get(k)
                return _dict
            return self._dict

        def __init__(self, d):
            if not isinstance(d, dict):
                return
            self._dict = d

        def __getattr__(self, item):
            return self._dict.get(item)

    class Processor:
        def __init__(self, processor, only_validate=False):
            self.processor = processor
            self.only_validate = only_validate

    """
    创建方法
    """

    def __init__(self, name, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name or name

        self.allow_null = False
        self.is_array = False
        self.default_value = Param.__NoDefault()

        self.processors = []
        self.children = []

    def __str__(self):
        return 'Param %s(%s), default=%s' % (self.name, self.verbose_name, self.default_value)

    @staticmethod
    def from_fields(fields: List[models.Field]):
        # return [Param.from_field(field) for field in fields]
        return tuple(map(Param.from_field, fields))

    @staticmethod
    def from_field(field: models.Field):
        param = Param(field.name, field.verbose_name)
        param.allow_null = field.null

        param.validate(SmartModel.field_validator(field))
        class_ = field.model
        validator = getattr(class_, '_valid_%s' % field.name, None)
        if callable(validator):
            param.validate(validator)
        return param

    @staticmethod
    def from_param(copied_param: object):
        if isinstance(copied_param, Param):
            return copied_param.clone()

    def clone(self):
        param = Param(self.name, self.verbose_name)
        param.default_value = self.default_value
        param.allow_null = self.allow_null
        param.is_array = self.is_array

        param.processors = self.processors[:]
        param.children = self.children
        return param

    def base(self):
        return Param(self.name, self.verbose_name)

    """
    参数赋值
    """

    def validate(self, validator, begin=False):
        if begin:
            self.processors.insert(0, Param.Processor(validator, only_validate=True))
        else:
            self.processors.append(Param.Processor(validator, only_validate=True))
        return self

    def process(self, processor, begin=False):
        if begin:
            self.processors.insert(0, Param.Processor(processor))
        else:
            self.processors.append(Param.Processor(processor))
        return self

    def default(self, v=None, allow_default=True):
        if allow_default:
            self.default_value = v
        else:
            self.default_value = self.__NoDefault
        return self

    def null(self, allow_null=True):
        self.allow_null = allow_null
        return self

    def sub(self, children: List[object]):
        self.children = []
        if isinstance(children, list):
            for param in children:
                if isinstance(param, Param):
                    self.children.append(param)
        return self

    def array(self, is_array=True):
        self.is_array = is_array
        return self

    def rename(self, name, verbose_name=None):
        self.name = name
        self.verbose_name = verbose_name or name
        return self

    def has_default(self):
        return not isinstance(self.default_value, Param.__NoDefault)

    @Packing.pack
    def run(self, value):
        if value is None:
            if self.allow_null:
                return None
            if self.has_default():
                value = self.default_value
            else:
                return BaseError.MISS_PARAM((self.name, self.verbose_name))

        if self.is_array:
            param = Param('%s/sub' % self.name, '%s/列表元素' % self.verbose_name).sub(self.children)
            if not isinstance(value, list):
                return BaseError.FIELD_FORMAT('%s不是列表' % self.verbose_name)
            for item_value in value:
                ret = param.run(item_value)
                if not ret.ok:
                    return ret
        else:
            for param in self.children:
                if not isinstance(value, dict):
                    return BaseError.FIELD_FORMAT('%s不存在子参数' % self.verbose_name)
                child_value = value.get(param.name)
                ret = param.run(child_value)
                if not ret.ok:
                    return ret

        for processor in self.processors:
            if processor.only_validate:
                # as a validator
                if isinstance(processor.processor, str):
                    if not re.match(processor.processor, str(value)):
                        return BaseError.FIELD_FORMAT('%s正则匹配失败' % self.verbose_name)
                elif callable(processor.processor):
                    try:
                        ret = processor.processor(value)
                        if not ret.ok:
                            return ret
                    except Exception as err:
                        return BaseError.FIELD_VALIDATOR(str(err))
            else:
                # as a processor
                if callable(processor.processor):
                    try:
                        ret = processor.processor(value)
                    except Exception as err:
                        return BaseError.FIELD_PROCESSOR(str(err))
                    if isinstance(ret, Packing):
                        if not ret.ok:
                            return ret
                        value = ret.body
                    else:
                        value = ret

        return value
