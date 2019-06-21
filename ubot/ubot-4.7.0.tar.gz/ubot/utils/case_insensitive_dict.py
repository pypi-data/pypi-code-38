class CaseInsensitiveDict(dict):
    @staticmethod
    def __lower_key(key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__convert_keys()

    def __getitem__(self, key):
        return super().__getitem__(self.__lower_key(key))

    def __setitem__(self, key, value):
        super().__setitem__(self.__lower_key(key), value)

    def __delitem__(self, key):
        return super().__delitem__(self.__lower_key(key))

    def __contains__(self, key):
        return super().__contains__(self.__lower_key(key))

    def pop(self, key, *args, **kwargs):
        return super().pop(self.__lower_key(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super().get(self.__lower_key(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super().setdefault(self.__lower_key(key), *args, **kwargs)

    def update(self, E=None, **F):
        if E is not None:
            super().update(self.__class__(E))
        if F:
            super().update(self.__class__(**F))

    def __convert_keys(self):
        for k in list(self.keys()):
            v = super().pop(k)
            self.__setitem__(k, v)
