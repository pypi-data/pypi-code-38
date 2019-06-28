class ListObject(list):

    def __init__(self, obj):
        super().__init__()
        self.obj = obj

    def append(self, obj_t):
        if isinstance(obj_t, self.obj):
            super().append(obj_t)
        else:
            raise Exception(
                "Given {} but required {}.".format(type(obj_t), type(self.obj)))

    def insert(self, index: int, obj_t):
        if isinstance(obj_t, self.obj):
            super().insert(index, obj_t)
        else:
            raise Exception(
                "Given {} but required {}.".format(type(obj_t), type(self.obj)))
