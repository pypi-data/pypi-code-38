from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer


class ChineseToNumberTransformer(ITransformer):
    """
    中文转数字
    """

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):
        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # 能进来的只能是字符串
        old_value = data[target_model_field.fieldName]

        if old_value is None:
            return {target_model_field.fieldName: None}

        import cn2an
        return {target_model_field.fieldName: cn2an.cn2an(old_value)}
