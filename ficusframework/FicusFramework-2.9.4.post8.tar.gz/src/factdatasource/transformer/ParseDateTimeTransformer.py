from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer

DATE_FORMAT_KEY = "__dateFormat__"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ParseDateTimeTransformer(ITransformer):
    """
    日期解析的转换器, 把字符串 转换成为 datetime
    """

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):

        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # 能进来的只能是字符串
        old_value = data[target_model_field.fieldName]

        if old_value is None:
            return {target_model_field.fieldName: None}

        date_format_string = params[DATE_FORMAT_KEY] if DATE_FORMAT_KEY in params else DEFAULT_DATE_FORMAT

        from datetime import datetime
        return {target_model_field.fieldName: datetime.strptime(old_value, date_format_string)}
