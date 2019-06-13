def pprint(obj):
    if not obj:
        return

    if isinstance(obj, str):
        print(obj)
        return

    for each in obj:
        print(each)
        print()


def pprint_nl(obj):
    if obj == None:
        return

    if isinstance(obj, str):
        print(obj)
        return

    for each in obj:
        print(each)


def plen(list_):
    if list_ == None or not isinstance(list_, (list, set)):
        raise Exception('None Type Object')

    return len(list_)


