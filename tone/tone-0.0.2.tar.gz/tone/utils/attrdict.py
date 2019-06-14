# coding=utf-8


class attrdict(dict):

    '''
    Use dict key as attribute if available
    '''

    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    @classmethod
    def loads(cls, value):
        if type(value) is dict:
            result = attrdict()
            result.update(value)
            for k, v in result.items():
                result[k] = cls.loads(v)

        elif type(value) is list:
            for index, item in enumerate(value):
                if type(item) in (list, dict):
                    value[index] = cls.loads(item)
            result = value
        else:
            result = value
        return result


class defaultattrdict(attrdict):

    '''
    like attrdict but if key not exists, then create a empty defaultattrdict.
    '''

    def __getattr__(self, key):
        try:
            return super(defaultattrdict, self).__getattr__(key)
        except AttributeError:
            self[key] = defaultattrdict()
            return self[key]

    def get(self, key):
        try:
            return self[key]
        except KeyError as e:
            self[key] = defaultattrdict()
            return self[key]
