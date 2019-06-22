class FundBase:

    def __init__(self, id, name=None):
        self.__id = id
        if name is None:
            self.__name = id
        else:
            self.__name = name

    def get(self):
        return None

    def csv_url(self):
        return None

    def detail_url(self):
        return None

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def __str__(self):
        return "%s, %s" % (self.id, self.name)
