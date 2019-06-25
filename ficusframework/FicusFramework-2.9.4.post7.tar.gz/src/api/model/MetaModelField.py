from enum import Enum

_defaultValues = {'STRING': "''", 'INTEGER': '0', 'LONG': '0', 'FLOAT': '0', 'DOUBLE': '0', 'BOOLEAN': "''",
                  'DATE': 'CURRENT_TIMESTAMP()', 'CHAR': "''", 'BYTE': "''", 'MODEL': "''"}


class DataTypeEnum(Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    LONG = "LONG"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    CHAR = "CHAR"
    BYTE = "BYTE"
    MODEL = "MODEL"

    def __new__(cls, name):
        obj = object.__new__(cls)
        obj._value_ = name
        obj._default_ = _defaultValues.get(name)
        return obj

    def default_value(self):
        return self._default_


class MetaModelField:
    def __init__(self, id=None, modelId=None, fieldName=None, alias=None, description=None,
                 dataType=None,
                 primaryKey=None, minLength=None, maxLength=None,
                 nullable=True, refModel=None, multiple=None, indexNames=None, fixItemId=None, params=None):
        self.id = id
        self.modelId = modelId
        self.fieldName = fieldName
        self.alias = alias
        self.description = description
        self.dataType: DataTypeEnum = DataTypeEnum(dataType)
        self.primaryKey = primaryKey
        self.minLength = minLength
        self.maxLength = maxLength
        self.nullable = nullable
        self.refModel = refModel
        self.multiple = multiple
        self.indexNames = indexNames
        self.fixItemId = fixItemId
        self.params = params

#
# if __name__ == '__main__':
#     a = DataTypeEnum("INTEGER")
#     print(f"{a} 默认值:{a.default_value()}")
#
#     b = DataTypeEnum('FLOAT')
#     print(f"{b} 默认值:{b.default_value()}")
#
#     c = DataTypeEnum('DATE')
#     print(f"{c} 默认值:{c.default_value()}")