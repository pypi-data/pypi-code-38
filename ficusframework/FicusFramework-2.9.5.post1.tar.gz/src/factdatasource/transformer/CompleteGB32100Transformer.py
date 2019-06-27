from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer


class CompleteGB32100Transformer(ITransformer):
    """
    社会统一代码补全 先不做
    """

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):
        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # TODO 这个先不实现

        return {target_model_field.fieldName: data[target_model_field.fieldName]}
