import unittest

from queryset_gallery.filters import Filter
from queryset_gallery.gallery import Gallery
from queryset_gallery.paginator import Paginator


def get_pagination_data(objects_count, page_number, page_count, per_page, errors=False):
    p = {
        'page_number': page_number,
        'per_page': per_page,
        'page_count': page_count,
        'objects_count': objects_count,
    }
    not errors or p.update({'errors': True})
    return p


class TestPaginator(unittest.TestCase):

    def setUp(self):
        self. objects = [i for i in range(1, 11)]

    def test_is_page_valid(self):
        params = ((1, 1, 8, 8, True),  (4, 2, 4, 8, True),  (5, 2, 5, 9, True), (0, 5, 2, 8, False),
                  (1, 1, 0, 0, True),  (2, 1, 0, 0, True),  (1, 2, 0, 0, True), (0, 1, 0, 0, False),
                  (0, 0, 0, 0, False), (1, 0, 0, 0, False), (0, 3, 3, 8, False))
        for p in params:
            self.assertEqual(
                Paginator._is_page_valid(
                    necessary_page=p[0], per_page=p[1], page_count=p[2], objects_count=p[3]
                ), p[4],
                msg=p
            )

    def test_calculate_index(self):
        params = ((1, 1, 1, (0, 1)), (1, 2, 2, (0, 2)), (4, 2, 8, (6, 8)),
                  (8, 1, 8, (7, 8)), (1, 1, 0, (0, 0)))
        for p in params:
            self.assertEqual(
                Paginator._calculate_index(
                    necessary_page=p[0], per_page=p[1], objects_count=p[2]
                ), p[3],
                msg=p
            )

    def test_get_objects_for_page(self):
        params = ((1, 1, [1]), (10, 1, [10]), (5, 2, [9, 10]), (4, 3, [10]), (1, 10, self.objects))
        for p in params:
            paginator = Paginator(objects=self.objects, per_page=p[1])
            self.assertEqual(
                paginator._get_objects_for_page(page_number=p[0]), p[2],
                msg=p
            )

    def test_get_page(self):
        params = (
            (1, 1, ([1], get_pagination_data(10, 1, 10, 1))),
            (0, 3, ([], get_pagination_data(10, 0, 4, 3, errors=True))),
            (2, 3, ([4, 5, 6], get_pagination_data(10, 2, 4, 3)))
        )
        for p in params:
            paginator = Paginator(objects=self.objects, per_page=p[1])
            self.assertEqual(
                paginator.get_page(page_number=p[0]), p[2],
                msg=p
            )


class TestGallery(unittest.TestCase):

    def setUp(self):
        class RemoveNumberFilter(Filter):
            def _execute(self, objects, param):
                return [i for i in objects if i != param]

        self.filter = RemoveNumberFilter(key='remove')

        class RemoveNumberGallery(Gallery):
            filters = [self.filter]

        self.gallery = RemoveNumberGallery()

    def test_apply_filters(self):
        self.assertEqual(self.filter.apply(objects=[1, 2, 3], param=3), [1, 2])
        self.assertEqual(
            self.filter.apply_from_dict_params(
                objects=[1, 3, 3], params={'remove': 3}
            ), [1]
        )
        self.assertEqual(
            self.filter.apply_from_dict_params(
                objects=[1, 3, 3], params={'number': 3}
            ), [1, 3, 3]
        )

    def test_get_page(self):
        self.assertEqual(
            self.gallery.get_page(
                objects=[1, 3, 2], filter_params={'remove': 3}, page_number=1, per_page=5),
            ([1, 2], get_pagination_data(2, 1, 1, 5))
        )
        self.assertEqual(
            self.gallery.get_page(
                objects=[1, 3, 2], filter_params={'remove': 3}, page_number=10, per_page=5),
            ([], get_pagination_data(2, 10, 1, 5, errors=True))
        )


if __name__ == '__main__':
    unittest.main()
