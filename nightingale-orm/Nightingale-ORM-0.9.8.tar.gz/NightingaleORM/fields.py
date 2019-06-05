
from NightingaleORM import dbmodel
import re,datetime


class Field:
    def __init__(self, name, column_type, primary_key, default):
        self.name = name  # 字段名
        self.column_type = column_type  # 字段数据类型
        self.primary_key = primary_key  # 是否是主键
        self.default = default  # 有无默认值

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)

    def __lt__(self, rhs):
        return dbmodel.ConditionModel(self, '<', rhs)

    def __le__(self, rhs):
        return dbmodel.ConditionModel(self, '<=', rhs)

    def __gt__(self, rhs):
        return dbmodel.ConditionModel(self, '>', rhs)

    def __ge__(self, rhs):
        return dbmodel.ConditionModel(self, '>=', rhs)

    def __eq__(self, rhs):
        return dbmodel.ConditionModel(self, '=', rhs)

    def __ne__(self, rhs):
        return dbmodel.ConditionModel(self, '!=', rhs)

    @staticmethod
    def fieldTest(feild, value):
        '''
        return a ture value
        '''
        if value is None:
            return feild.default
        if isinstance(feild,StringField):
            if not isinstance(value, str):
                return feild.default
            containList = re.findall(r'[^()]+', feild.column_type)
            size = 0
            if len(containList) > 1:
                size = int(containList[1])
            if size > 0:
                if len(value) > size:
                    return value[:size]
                return value
            return value
        elif isinstance(feild,IntegerField):
            if not isinstance(value, int):
                return feild.default
            if 'int' in feild.column_type:
                if not (-2147483648 < value <2147483647 ):
                    return feild.default
            return value
        elif isinstance(feild,FloatField):
            if not isinstance(value, float):
                return feild.default
            return value
        elif isinstance(feild,DateTimeField):
            if isinstance(value, datetime.datetime):
                return value 
            if isinstance(value,str):
                try:
                    return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                except :
                    pass
            return feild.default

        return value


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(128)'):
        super(StringField, self).__init__(name, ddl, primary_key, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='bigint'):
        super(IntegerField, self).__init__(name, ddl, primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='float'):
        super(FloatField, self).__init__(name, ddl, primary_key, default)


class DateTimeField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='datetime)'):
        super(DateTimeField, self).__init__(name, ddl, primary_key, default)
