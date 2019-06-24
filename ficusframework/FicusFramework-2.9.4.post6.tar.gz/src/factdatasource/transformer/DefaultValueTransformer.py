from datetime import datetime

from api.model.MetaModelField import MetaModelField, DataTypeEnum
from factdatasource.transformer.ITransformer import ITransformer

DATE_FORMAT_KEY = "__dateFormat__"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_VALUE_KEY = "__default_value__"
NOW = "now()"


class DefaultValueTransformer(ITransformer):
    """
    默认值的转换器,
    """

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):
        if (params is None or len(params) == 0) or (
                DEFAULT_VALUE_KEY not in params or params[DEFAULT_VALUE_KEY] is None or params[
            DEFAULT_VALUE_KEY] == ""):

            # 没有设置默认值,不管他
            if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
                return {target_model_field.fieldName: None}

            return data[target_model_field.fieldName]

        old_value = data[target_model_field.fieldName]

        # 默认值,String的
        default_string = params[DEFAULT_VALUE_KEY]

        # 需要根据字段类型进行变更
        # 找到目标字段类型
        data_type = target_model_field.dataType

        if data_type == DataTypeEnum.STRING:
            return {target_model_field.fieldName: default_string if old_value is None else old_value}
        elif data_type in [DataTypeEnum.FLOAT, DataTypeEnum.LONG, DataTypeEnum.INTEGER, DataTypeEnum.DOUBLE]:
            return {target_model_field.fieldName: self.__inner_number_convert(old_value, data_type, default_string)}
        elif data_type == DataTypeEnum.DATE:
            return {target_model_field.fieldName: self.__inner_date_convert(old_value,
                                             DEFAULT_DATE_FORMAT if DATE_FORMAT_KEY not in params else params[
                                                 DATE_FORMAT_KEY], default_string)}
        elif data_type == DataTypeEnum.BOOLEAN:
            return {target_model_field.fieldName: self.__inner_boolean_convert(old_value, default_string)}
        elif data_type == DataTypeEnum.CHAR:
            return {target_model_field.fieldName: self.__inner_char_convert(old_value, default_string)}
        elif data_type == DataTypeEnum.BYTE:
            return {target_model_field.fieldName: self.__inner_byte_convert(old_value, default_string)}

    def __inner_number_convert(self, old_value, data_type, default_string):
        if old_value is not None:
            return old_value

        if data_type == DataTypeEnum.Long or data_type == DataTypeEnum.INTEGER:
            return int(default_string)
        elif data_type == DataTypeEnum.FLOAT or data_type == DataTypeEnum.DOUBLE:
            return float(default_string)

        return None

    def __inner_date_convert(self, old_value, date_format, default_string):
        if old_value is not None:
            return old_value

        if NOW == default_string:
            return datetime.now().strftime(DEFAULT_DATE_FORMAT)
        else:
            return datetime.strptime(default_string, date_format)

    def __inner_boolean_convert(self, old_value, default_string):
        if old_value is not None:
            return old_value

        return bool(default_string)

    def __inner_char_convert(self, old_value, default_string):
        if old_value is not None:
            return old_value

        return default_string[0]

    def __inner_byte_convert(self, old_value, default_string: str):
        if old_value is not None:
            return old_value

        if default_string.lower().startswith("0x"):
            return int(default_string[2:])
        else:
            return int(default_string)
