
def listInsertAfter(lst, a, b):
    """ insert a after b, if b not exist then append last """
    for index, data in enumerate(lst):
        if data == b:
            lst.insert(index+1, a)
            return
    lst.append(a)


def listGetFirstDuplicateItem(lst):
    itemSet = set()
    for item in lst:
        if item in itemSet:
            return item
        itemSet.add(item)
    return None


def listUnique(lst):
    newLst = []
    for item in lst:
        if item not in newLst:
            newLst.append(item)
    lst[:] = newLst


def listRemoveAll(lst, item):
    while item in lst:
        lst.remove(item)