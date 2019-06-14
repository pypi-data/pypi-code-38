required = { 'require_me': True }

class RecordClass(dict):

    def __init__(self, defaults, **kwargs):
        self.update(defaults)
        init_values = dict(**kwargs)
        for key, value in init_values.items():
            if key in self:
                self[key] = value
            else:
                raise KeyError(key)
        for key, value in self.items():
            if value == required:
                raise KeyError(f'{key} is required!')

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key not in self:
            raise KeyError(key)
        self[key] = value

class Record:

    def __init__(self, defaults):
        self.defaults = defaults
        self.keys     = defaults.keys()

    def __call__(self, **kwargs):
        return RecordClass(self.defaults, **kwargs)
