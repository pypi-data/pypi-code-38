from operator import setitem

import scrapy


def attr_settler(cls, obj):
    item = cls()
    if not isinstance(item, scrapy.Item):
        msg = ("(%s) is not supported now, we only support the types in items.py. Let sb knows if you want others." %
               type(item).__name__)
        raise Exception(msg)
    field_keys = item.fields.keys()
    for key in field_keys:
        if key in obj:
            v = obj[key]
            if key == 'id':
                #  MongoDB can only handle up to 8-byte ints
                v = str(v)
            setitem(item, key, v)
    return item
