
def VBase(object):
    def __init__(self):
        self.children = None

    def attach(self, node):
        self.children.append(node)


def Cube(VBase):
    def __init__(self, name, physical_table):
        super(Cube, self).__init__(self)
        self.name = name
        self.physical_table = physical_table


def Dimension(VBase):
    def __init__(self, name, physical_table=None, foreignKey=None):
        self.name = name
        self.physical_table = physical_table
        self.foreignKey = foreignKey


def Hierarchy(VBase):
    def __init__(self, name, hasAll=True):
        self.name = name
        self.hasAll = hasAll


def Level(VBase):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key not in ["name", "nameColumn", "column", "ordinal", "uniqueMembers"]:
                raise ValueError("bad value for key", key)
            setattr(self, key, val)


def Measure(VBase):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


def CalculatedMember(VBase):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)
