from api.model.MetaModelField import MetaModelField
from factdatasource.transformer.ITransformer import ITransformer


class FixItemTransformer(ITransformer):

    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField):
        # 如果没有这个字段就不管他

        if (data is None or len(data) == 0) or target_model_field.fieldName not in data:
            return {target_model_field.fieldName: None}

        # 能进来的只能是字符串
        old_value = data[target_model_field.fieldName]

        # 逻辑是这样的, 从params里面找到这个值得结果, 如果是 null 那么params中的key就是 null
        if old_value is None:
            return {target_model_field.fieldName: params["null"] if "null" in params else None}

        # 现在暂时先只支持 等于的方式的受控词. 以后再支持范围等方式的受控词

        return {target_model_field.fieldName: params[old_value] if old_value in params else old_value}
