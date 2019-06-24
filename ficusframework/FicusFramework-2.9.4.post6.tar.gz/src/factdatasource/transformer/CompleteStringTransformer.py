from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer

PREFIX = "__prefix__"
SUFFIX = "__suffix__"


class CompleteStringTransformer(ITransformer):

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):
        # 如果没有这个字段就不管他
        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # 能进来的只能是字符串
        old_value = data[target_model_field.fieldName]

        if old_value is None:
            return {target_model_field.fieldName: None}

        prefix = params[PREFIX] if PREFIX in params else ""
        suffix = params[SUFFIX] if SUFFIX in params else ""

        return {target_model_field.fieldName: f"{prefix}{old_value}{suffix}"}
