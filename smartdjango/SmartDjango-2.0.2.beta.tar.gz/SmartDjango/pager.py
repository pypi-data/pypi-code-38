from .model import SmartQuerySet


class Page:
    def __init__(self, object_list, next_value, total_count):
        self.object_list = object_list
        self.next_value = next_value
        self.total_count = total_count

    def dict(self, object_dictor=None, next_dictor=None):
        if callable(object_dictor):
            object_list = list(map(object_dictor, self.object_list))
        else:
            object_list = self.object_list
        if callable(next_dictor):
            next_value = next_dictor(self.next_value)
        else:
            next_value = self.next_value
        return dict(
            object_list=object_list,
            next_value=next_value,
            total_count=self.total_count,
        )


class SmartPager:
    FILTER_FIRST = 1
    CHOOSE_AMONG = 2

    def __init__(self, mode=FILTER_FIRST, compare_field='pk', ascend=True, order_by=None):
        self.mode = mode
        if self.mode == self.FILTER_FIRST:
            self.compared_field = compare_field
            self.filter_key = '%s__%st' % (compare_field, 'lg'[ascend])
            self.order_by = compare_field
            if not ascend:
                self.order_by = '-' + compare_field
            self.order_by = (self.order_by, )
        else:
            self.order_by = order_by

    def page(self, queryset: SmartQuerySet, last=0, count=5):
        total_count = queryset.count()
        if self.mode == self.FILTER_FIRST:
            objects = queryset.filter(**{self.filter_key: last}).order_by(*self.order_by)
            page_count = objects.count()
            if page_count > count:
                objects = objects[:count]
                _next = getattr(objects[count-1], self.compared_field)
            else:
                _next = None
        else:
            objects = queryset.order_by(*self.order_by)
            objects = objects[last:]
            page_count = objects.count()
            if page_count > count:
                objects = objects[:count]
                _next = last + count
            else:
                _next = None
        return Page(objects, _next, total_count)
