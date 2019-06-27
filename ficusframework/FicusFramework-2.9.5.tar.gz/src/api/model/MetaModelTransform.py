from enum import Enum


class TransformSourceTypeEnum(Enum):
    FIELD = "FIELD",  # 字段, 如果是这种, 那么在FD最终写入数据库的时候, 会再通过这个转换器转换一次结果
    MAPPING = "MAPPING"  # 映射, 如果是这种, 那么在映射转换过程中, 会通过这个转换器转换一次结果, 不填就是完整拷贝源的值到目标, 如果源的值是多个, 根据目标字段类型决定默认值是什么, 字符串默认为空格拼接 数字是相加 布尔是且 日期取最大


def init_transform_by_field(id):
    from factdatasource.dao.jdbc.JdbcDatasourceDao import JdbcDatasourceDao
    dao = JdbcDatasourceDao.instance()
    sql = f"""SELECT id,sourceType,sourceId,transformer,params,orders,updateTime FROM `sc_metamodel_transform` WHERE id=:id and sourceType = 'FIELD'"""
    code_dict = {'id': id}
    rows = dao.select_all(sql, code_dict)

    if rows is not None and len(rows) > 0:
        return [MetaModelTransform(model["id"], model["sourceType"], model["sourceId"], model["transformer"],
                                   model["params"],
                                   model["orders"], model["updateTime"]) for model in rows]

    return None


class MetaModelTransform:

    def __init__(self, id=None, sourceType=None, sourceId=None, transformer=None, params=None, orders=None,
                 updateTime=None):
        self.id = id
        self.sourceType: TransformSourceTypeEnum = sourceType
        self.sourceId = sourceId
        self.transformer = transformer
        self.orders = orders
        self.updateTime = updateTime
        if params:
            import json
            self.params = json.loads(params)

    def __str__(self) -> str:
        return f"{self.transformer}_{self.sourceType}_{self.sourceId}_{self.id}"

    def timeString(self) -> str:
        if self.updateTime is None:
            import datetime
            return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        else:
            return self.updateTime.strftime("%Y%m%d%H%M%S%f")
