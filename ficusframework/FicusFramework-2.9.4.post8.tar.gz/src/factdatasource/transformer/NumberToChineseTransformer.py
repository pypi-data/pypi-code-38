from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer

LETTER_CASE_KEY = "__case__"


class NumberToChineseTransformer(ITransformer):
    """
    数字转中文的处理器
    """

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):

        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # 能进来的只能是字符串
        old_value = data[target_model_field.fieldName]

        if old_value is None:
            return {target_model_field.fieldName: None}

        # 获取大小写
        letter_case = params[LETTER_CASE_KEY] if LETTER_CASE_KEY in params else "lower"

        import cn2an
        return {target_model_field.fieldName: cn2an.an2cn(old_value, letter_case == "upper")}
