# -*- coding: utf-8 -*-

import uuid
import re
from marshmallow import ValidationError
from ..lib.CommonLogger import debug, info, warn, error
from .validator import validator
from .validator import validator_match_dict
from marshmallow import fields, schema

schema_fields_match = {
    'field': fields.Field,
    'raw': fields.Raw,
    'nested': fields.Nested,
    'dict': fields.Dict,
    'object': fields.Dict,
    'json': fields.Dict,
    'list': fields.List,
    'string': fields.String,
    'uuid': fields.UUID,
    'number': fields.Number,
    'integer': fields.Integer,
    'decimal': fields.Decimal,
    'boolean': fields.Boolean,
    'formattedstring': fields.FormattedString,
    'float': fields.Float,
    'datetime': fields.DateTime,
    'localdatetime': fields.LocalDateTime,
    'time': fields.Time,
    'date': fields.Date,
    'timedelta': fields.TimeDelta,
    'url': fields.Url,
    'email': fields.Email,
    'method': fields.Method,
    'function': fields.Function,
    'str': fields.Str,
    's': fields.String,
    'bool': fields.Bool,
    'b': fields.Bool,
    'int': fields.Int,
    'i': fields.Int,
    'constant': fields.Constant,
}


class SchemaGenerator(object):
    """
    动态模板，每一个API会生成一个
    """

    def _generate_obj_cfg(self, params_cfg):
        """
        生成类一个类需要的配置字典
        :param params_cfg: 参数的配置字典
        :return: dict
        """
        result_dict = {}
        for one_param in params_cfg:
            param_name = one_param.get('id')
            param_type_s = one_param.get('type')
            param_type = schema_fields_match.get(param_type_s)
            if param_type is None:
                error("{} 不存在类型: {}".format(param_name, param_type_s))
                continue
            is_required = one_param.get('required', '').lower() == 'true'
            default_value = one_param.get('default')
            if default_value and is_required:
                # 有默认值,那么就是可选的了
                is_required = False
            one_param_valid = validator.get_validators(one_param)
            result_dict[param_name] = param_type(
                default=default_value,
                required=is_required,
                validate=one_param_valid,
                allow_none=True,
            )

        return result_dict

    def generate_schema(self, params_cfg):
        """
        根据参数配置生成需要的schema对象
        :param params_cfg:
        :return:
        """
        class_cfg_dict = self._generate_obj_cfg(params_cfg)
        custom_uuid_class = "cls_schema_{}".format(re.sub("-", "_", str(uuid.uuid1())))
        debug("生成的内置类名是: {},类配置是:{}".format(custom_uuid_class, class_cfg_dict))
        the_schema = type(custom_uuid_class, (schema.Schema,), class_cfg_dict)
        return the_schema()


schema_generator = SchemaGenerator()
