
class SchemaObj:

    def __init__(self, data):
        self.data = data

    def get_schema(self):
        return self.data[1]

    def get_table_name(self):
        return self.data[2]

    def get_name(self):
        return self.data[3]

    def get_position(self):
        return self.data[4]

    def get_default(self):
        return self.data[5]

    def is_nullable(self):
        return self.data[6] == 'YES'

    def get_type(self):
        return self.data[7]

    def get_length(self):
        return self.data[8]

    def get_numeric_precision(self):
        return self.data[10]

    def is_primary(self):
        return self.data[16] == 'PRI'

    def get_def_text(self):
        name = self.get_name()
        type = self.get_type()
        map_type = {
            'bigint': 'BigIntegerField',
            'blob': 'BlobField',
            'varchar': 'CharField',
            'tinyint': 'SmallIntegerField',
            'timestamp': 'TimestampField',
            'text': 'TextField',
            'mediumtext': 'TextField',
            'datetime': 'DateTimeField',
            'date': 'DateField',
            'float': 'FloatField',
            'double': 'DoubleField',
            'decimal': 'DecimalField',
        }

        if type == 'int':
            if self.get_numeric_precision() < 11:
                line = '%s = IntegerField()' % name
            else:
                line = '%s = BigIntegerField()' % name
        else:
            type_ = map_type.get(type)
            if not type_:
                raise Exception('Not found type for get_def_text: %s' % type)
            line = '%s = %s()' % (name, type_)

        return '\t' + line + '\n'