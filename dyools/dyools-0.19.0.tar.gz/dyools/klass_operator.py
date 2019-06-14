from __future__ import (absolute_import, division, print_function, unicode_literals)

from .klass_is import IS


class Operator(object):
    @classmethod
    def flat(cls, *lists):
        result = []

        def put_in(item):
            if IS.iterable(item):
                for x in item:
                    put_in(x)
            else:
                result.append(item)

        for item in lists:
            put_in(item)
        return result

    @classmethod
    def unique(cls, sequence):
        result = []
        if IS.iterable(sequence):
            for item in sequence:
                found = False
                for res in result:
                    if res == item and type(res) == type(item):
                        found = True
                        break
                if not found:
                    result.append(item)
        else:
            return sequence
        return result

    @classmethod
    def split_and_flat(cls, sep=',', *lists):
        result = cls.flat(lists)
        for i, item in enumerate(result):
            if IS.str(item):
                result[i] = item.split(sep)
        return cls.flat(result)

    @classmethod
    def intersection(cls, *lists):
        result = []
        if len(lists) > 1:
            part1, part2 = lists[0], lists[1:]
            for item1 in part1:
                found = True
                for list2 in part2:
                    if item1 not in list2:
                        found=False
                if found:
                    result.append(item1)
        elif len(lists) == 1:
            result = lists[0]
        return result


    @classmethod
    def unique_intersection(cls, *lists):
        result = []
        items = cls.flat(lists)
        items = cls.unique(items)
        for item in items:
            if all([item in x for x in lists]):
                result.append(item)
        return cls.unique(result)
