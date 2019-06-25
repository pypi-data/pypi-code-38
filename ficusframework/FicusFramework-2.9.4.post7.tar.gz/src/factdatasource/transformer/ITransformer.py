from abc import abstractmethod

from api.model.MetaModelField import MetaModelField


class ITransformer:
    """
    数据字段的转换接口
    """

    @abstractmethod
    def transform_field(self, data: dict, params: dict, target_model_field: MetaModelField) -> dict:
        """
        字段的值转换
        :param data: 源数据,
        :param params: 可能的转换参数
        :param target_model_field: 模型字段
        :param default_value: 默认值
        :return: 转换的结果, key是字段的名字, value是转换后的结果, 这里是一个Map的结果主要原因是,某一些转换器会把一个字段的结果转换成为多个字段,相当于是字段的分裂.因此需要使用Map来保存
        """
        pass
