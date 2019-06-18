

class Collection:

    total = 0
    objects = {}
    meta = None
    pointer = 0

    def __init__(self, objects=None, meta=None):
        """
        :param dict|None objects:
        :param Meta|None meta:
        """
        if objects:
            self.objects = objects

            try:
                self.total = len(objects)
            except BaseException:
                self.total = 1

        self.meta = meta

    def add(self, _object, id=None):
        """
        :param _object:
        :param id:
        """
        self.objects.update({(id or self.total): _object})
        self.total += 1

    def getByIndex(self, index: int):
        """
        :param int index:
        :return dict:
        """
        return self.getRow(index)

    def count(self):
        """
         Get current total of items in Collection
        :rtype int:
        """
        return self.total

    def asArray(self):
        """
        :rtype dict:
        """
        # TODO: Iterate  with other approach

        for item in self:
            pass

        return self.objects

    def getMeta(self):
        """
        :return Meta:
        """
        return self.meta

    def getRow(self, index: int):
        """
        :param int index:
        :return None or found object:
        """
        try:
            return self.objects[index]  # TODO test
        except BaseException:
            return None

    def current(self):
        """
        Return the current element
        :return:
        """
        return self.getRow(self.pointer)

    def next(self):
        """
        Move forward to next element
        """
        row = self.getRow(self.pointer)

        if row:
            self.pointer += 1

    def key(self):
        """
        Return the key of the current element
        """
        return self.pointer

    def valid(self):
        """
        Checks if current position is valid
        """
        isValid = (self.current() or False)

        if not isValid:
            self.pointer = 0
        return isValid

    def rewind(self):
        """
        Rewind the Iterator to the first element
        """
        self.pointer = 0