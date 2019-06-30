class Attribute:
    @staticmethod
    def dictor(o, field_list):
        d = dict()
        for field_name in field_list:
            if isinstance(field_name, tuple):
                arg = field_name[1:]
                field_name = field_name[0]
            else:
                arg = tuple()

            value = getattr(o, field_name, None)

            readable_func = getattr(o, '_readable_%s' % field_name, None)
            if callable(readable_func):
                value = readable_func(*arg)

            d[field_name] = value
        return d
