class Data(dict):
    def __init__(self):
        super().__init__()

    @property
    def usr(self):
        """ get usr property  """
        if 'usr' in self:
            return self['usr']

    @usr.setter
    def usr(self, usr):
        self['usr'] = usr

    @property
    def pwd(self):
        """ get pwd property """
        if 'pwd' in self:
            return self['pwd']

    @pwd.setter
    def pwd(self, pwd):
        self['pwd'] = pwd

    @property
    def authorization(self):
        if 'authorization' in self:
            return self['authorization']

    @authorization.setter
    def authorization(self, authorization):
        self['authorization'] = authorization

    @property
    def _items(self):
        """ get items property """
        if '_items' in self:
            return self['_items']

    @_items.setter
    def _items(self, items):
        self['_items'] = items

    @property
    def start_time(self):
        """ get start_time property """
        if 'start_time' in self:
            return self['start_time']

    @start_time.setter
    def start_time(self, start_time):
        self['start_time'] = start_time

    @property
    def end_time(self):
        """ get end_time property """
        if 'end_time' in self:
            return self['end_time']

    @end_time.setter
    def end_time(self, end_time):
        self['end_time'] = end_time

    @property
    def scr(self):
        """ get scr (script) property """
        if 'src' in self:
            return self['scr']

    @scr.setter
    def scr(self, scr):
        self['scr'] = scr

    @property
    def farg(self):
        """ get farg (function argument) property """
        if 'farg' in self:
            return self['farg']

    @farg.setter
    def farg(self, farg):
        self['farg'] = farg

    @property
    def func(self):
        """ get func (function name) property """
        if 'func' in self:
            return self['func']

    @func.setter
    def func(self, func):
        self['func'] = func

    @property
    def lib(self):
        """ get lib (library name) property """
        if 'lib' in self:
            return self['lib']

    @lib.setter
    def lib(self, lib):
        self['lib'] = lib

    @property
    def type(self):
        """ get type property """
        if 'type' in self:
            return self['type']

    @type.setter
    def type(self, _type):
        self['type'] = _type
