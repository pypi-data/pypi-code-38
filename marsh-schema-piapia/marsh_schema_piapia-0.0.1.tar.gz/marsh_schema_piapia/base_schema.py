space_4 = '    '
space_8 = f'{space_4}{space_4}'


def str2hump(s):
    arr = s.lower().split('_')
    if len(arr) == 1:
        return arr[0]
    else:
        res = ''
        for i in arr[1:]:
            res = res + i[0].upper() + i[1:]
        return arr[0] + res


def str2hump2(s):
    arr = s.lower().split('_')
    res = ''
    for i in arr:
        res = res + i[0].upper() + i[1:]
    return res


class BaseSchemaItem:

    SCHEMA_NAME = 'fields.String'

    def __init__(self, name, *, dump_to=None, load_from=None):
        self.name = name
        self.dump_to = dump_to
        self.load_from = load_from

    def code_gen(self):
        inner = []
        if self.dump_to:
            inner.append(f"dump_to='{self.dump_to}'")  # NOQA
        if self.load_from:
            inner.append(f"load_from='{self.dump_to}'")  # NOQA
        inner_str = ', '.join(inner) if inner else ''
        return f'{self.name} = {self.__class__.SCHEMA_NAME}({inner_str})'


class IntSchemaItem(BaseSchemaItem):

    SCHEMA_NAME = 'fields.Integer'


class BoolSchemaItem(BaseSchemaItem):

    SCHEMA_NAME = 'fields.Boolean'


class NestSchemaItem:

    SCHEMA_NAME = 'fields.Nested'

    def __init__(self, name, sub_schema_code_gen,
                 *, dump_to=None, load_from=None, many=True):
        self.name = name
        self.sub_schema_code_gen = sub_schema_code_gen
        self.dump_to = dump_to
        self.load_from = load_from
        self.many = many

    def code_gen(self):
        inner = [f'{self.sub_schema_code_gen.name}']
        if self.dump_to:
            inner.append(f"dump_to='{self.dump_to}'")  # NOQA
        if self.load_from:
            inner.append(f"load_from='{self.load_from}'")  # NOQA
        inner.append(f'many={self.many}')
        inner_str = ', '.join(inner)
        # code0 = self.sub_schema_code_gen.code_gen()
        code1 = f'{self.name} = {self.__class__.SCHEMA_NAME}({inner_str})'  # NOQA
        return f'{code1}'


class SchemaCodeGen:

    def __init__(self, name, item_list):
        self.name = name
        self.item_list = sorted(
            item_list,
            key=lambda x: isinstance(x, self.__class__) or isinstance(x, NestSchemaItem), reverse=True)  # NOQA

    def code_gen(self):
        inner_str = [f'class {str2hump2(self.name)}(Schema):']
        out_str = []
        for item in self.item_list:
            if isinstance(item, SchemaCodeGen) or isinstance(item, NestSchemaItem):  # NOQA
                out_str.append(item.code_gen())
                tmp = NestSchemaItem(
                    item.name, item, dump_to=str2hump(item.name),
                    load_from=str2hump(item.name))
                inner_str.append(f'{space_4}{tmp.code_gen()}')
                continue
            inner_str.append(f'{space_4}{item.code_gen()}')
        out_str.append('\n'.join(inner_str))
        return '\n\n'.join(out_str)


def dict2schemas(paras, name):
    item_list = []
    for k in paras:
        v = paras[k]
        item = None
        if isinstance(v, SchemaCodeGen) or isinstance(v, NestSchemaItem):
            item = NestSchemaItem(
                str(k), v, dump_to=str2hump(str(k)),
                load_from=str2hump(str(k)))
        elif isinstance(v, int):
            item = IntSchemaItem(
                str(k), dump_to=str2hump(str(k)), load_from=str2hump(str(k)))
        elif isinstance(v, bool):
            item = BoolSchemaItem(
                str(k),
                dump_to=str2hump(str(k)), load_from=str2hump(str(k)))
        elif isinstance(v, dict):
            item = dict2schemas(v, k)
        elif isinstance(v, list):
            item = dict2schemas(v[0], k)
        else:
            item = BaseSchemaItem(
                str(k),
                dump_to=str2hump(str(k)), load_from=str2hump(str(k)))
        item_list.append(item)
    return SchemaCodeGen(name, item_list)
