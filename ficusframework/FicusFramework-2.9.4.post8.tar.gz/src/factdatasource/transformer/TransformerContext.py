from typing import Optional

from api.handler.script import ScriptPythonFactory
from api.model.MetaModelTransform import MetaModelTransform
from factdatasource.transformer.ChineseToNumberTransformer import ChineseToNumberTransformer
from factdatasource.transformer.CompleteGB32100Transformer import CompleteGB32100Transformer
from factdatasource.transformer.CompleteStringTransformer import CompleteStringTransformer
from factdatasource.transformer.DefaultValueTransformer import DefaultValueTransformer
from factdatasource.transformer.FixItemTransformer import FixItemTransformer
from factdatasource.transformer.ITransformer import ITransformer
from factdatasource.transformer.NumberToChineseTransformer import NumberToChineseTransformer
from factdatasource.transformer.ParseDateTimeTransformer import ParseDateTimeTransformer

__instance = {
    "DefaultValue": DefaultValueTransformer(),
    "FixItem": FixItemTransformer(),
    "CompleteString": CompleteStringTransformer(),
    "ParseDate": ParseDateTimeTransformer(),
    "ChineseToNumber": ChineseToNumberTransformer(),
    "NumberToChinese": NumberToChineseTransformer(),
    "CompleteGB32100": CompleteGB32100Transformer(),
    "CustomTransformer": None
}


def get_transformer(transformer: MetaModelTransform) -> Optional[ITransformer]:
    transformer_name = transformer.transformer

    if transformer_name not in __instance:
        return None

    if "CustomTransformer" == transformer_name:
        # TODO 如果是自定义的转换器,那么就需要实例化
        source_code = transformer.params["__sourceCode__"]
        key = f"{str(transformer)}_{transformer.timeString()}"
        for name, instance in __instance.items():
            if name.startswith(str(transformer)):
                # 说明是同一个,然后就看时间是否是一样的
                if name == key:
                    # 时间都是一样的,说明是同一个,直接返回
                    return instance
                else:
                    # 说明是同一个转换器,但时间不同,需要重新加载
                    ScriptPythonFactory.destroy_instance(key)

        instance = ScriptPythonFactory.load_instance(key, source_code, "ITransformer")
        __instance[key] = instance
        return instance
    else:
        return __instance[transformer_name]
