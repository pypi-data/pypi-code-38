# -*- coding: utf-8 -*-


def parse_sort_string(sort):
    """
    Parse a sort string for use with the db

    :param: sort: the sort string
    """
    if sort is None:
        return []
    else:
        l = sort.rsplit(',')
        sortlist = []
        for se in l:
            order = 'desc' if se[0:1] == '-' else 'asc'
            field = se[1:] if se[0:1] in ['-', '+'] else se
            field = field.strip()
            sortlist.append((field, order))
        return sortlist
