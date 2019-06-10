# -*- coding: utf-8 -*-

from marshmallow import ValidationError
from ..lib.CommonLogger import debug, info, warn, error
from marshmallow.fields import Field
from marshmallow.validate import (
    URL, Email, Range, Length, Equal, Regexp,
    Predicate, NoneOf, OneOf, ContainsOnly
)

from .validators import (
    RangeValid, LengthValid, RegexpValid,
    NoneOfValid, OneOfValid, ContainsOnlyValid
)

URL.default_message = '无效的链接'
Email.default_message = '无效的邮箱地址'
Range.message_min = '不能小于{min}'
Range.message_max = '不能小于{max}'
Range.message_all = '不能超过{min}和{max}这个范围'
Length.message_min = '长度不得小于{min}位'
Length.message_max = '长度不得大于{max}位'
Length.message_all = '长度不能超过{min}和{max}这个范围'
Length.message_equal = '长度必须等于{equal}位'
Equal.default_message = '必须等于{other}'
Regexp.default_message = '非法输入'
Predicate.default_message = '非法输入'
NoneOf.default_message = '非法输入'
OneOf.default_message = '无效的选择'
ContainsOnly.default_message = '一个或多个无效的选择'

Field.default_error_messages = {
    'required': '该字段是必填字段',
    'type': '无效的输入类型',
    'null': '字段不能为空',
    'validator_failed': '无效的值'
}

validator_match_dict = {
    'regexp': RegexpValid,
    'range': RangeValid,
    'length': LengthValid,
    'values': OneOfValid,
    'none-of': NoneOfValid,
    'contains-only': ContainsOnlyValid
}


class Validator(object):
    """
    校验入口，用于校验
    """

    def _generate_one_validator(self, validator_key, param_str):
        v_class = validator_match_dict.get(validator_key)
        debug("创建校验[{}]类:{}".format(validator_key, v_class))
        return v_class(param_str)

    def get_validators(self, one_param):
        validators = []
        for one_key in validator_match_dict.keys():
            if one_key in one_param:
                one_validator = self._generate_one_validator(one_key, one_param.get(one_key))
                validators.append(one_validator)
        return validators

    def validate(self, schema, kwargs):
        try:
            # 校验
            schema.load(kwargs)
            # 设置默认值
            result = schema.dump(kwargs)
            return result
        except ValidationError as err:
            if isinstance(err.message, dict):
                for k, v in err.message.items():
                    if isinstance(v, list):
                        msg = " & ".join(v)
                    else:
                        msg = v
                    warn("校验参数[{}]出现错误:{}".format(k, msg))
            else:
                warn("校验出现参数:{},出现错误:{}".format(kwargs, err.message))
            raise err


validator = Validator()
