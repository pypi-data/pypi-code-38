def list_except(self, remove):
    return [x for x in self if (x not in remove)]

def str_listify(self):
    if isinstance(self, str):
        return [self]
    else:
        return self