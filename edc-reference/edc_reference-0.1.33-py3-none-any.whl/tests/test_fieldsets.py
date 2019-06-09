from django.test import TestCase, tag

from ..refsets import Fieldset, FieldsetError


class DummyRefset:
    def __init__(self, i):
        self.f1 = i
        self.f2 = "filter"[i]


class TestFieldset(TestCase):
    def setUp(self):
        refsets = []
        for i in range(0, 5):
            refsets.append(DummyRefset(i))
        self.fieldset = Fieldset(field="f1", refsets=refsets)

    def test_all(self):
        self.assertEqual(list(self.fieldset.all()), [0, 1, 2, 3, 4])

    def test_all_chained_to_orderby(self):
        self.assertEqual(list(self.fieldset.all().order_by("-f1")), [4, 3, 2, 1, 0])

    def test_filter(self):
        self.assertEqual(list(self.fieldset.filter(2)), [2])

    def test_filter_none(self):
        self.assertEqual(list(self.fieldset.filter()), [0, 1, 2, 3, 4])

    def test_filter_chained_to_orderby(self):
        self.assertEqual(list(self.fieldset.filter(2, 3, 4).order_by("-f1")), [4, 3, 2])

    def test_orderby_nothing(self):
        self.fieldset._refsets = []
        self.assertEqual(list(self.fieldset.order_by()), [])

    def test_first_last(self):
        self.assertEqual(self.fieldset.first(), 0)
        self.assertEqual(self.fieldset.last(), 4)
        self.assertEqual(self.fieldset.first(2), 2)
        self.assertEqual(self.fieldset.last(2), 2)
        self.assertEqual(self.fieldset.first(999), None)
        self.assertEqual(self.fieldset.last(999), None)
        self.assertEqual(self.fieldset.order_by("-f1").first(), 4)
        self.assertEqual(self.fieldset.order_by("-f1").last(), 0)

    def test_order_asc(self):
        self.assertEqual(list(self.fieldset.all().order_by("f1")), [0, 1, 2, 3, 4])

    def test_order_desc(self):
        self.assertEqual(list(self.fieldset.all().order_by("-f1")), [4, 3, 2, 1, 0])

    def test_order_asc_by_f2(self):
        self.assertEqual(list(self.fieldset.all().order_by("f2")), [4, 0, 1, 2, 3])

    def test_order_desc_by_f2(self):
        self.assertEqual(list(self.fieldset.all().order_by("-f2")), [3, 2, 1, 0, 4])

    def test_order_raises(self):
        self.assertRaises(FieldsetError, self.fieldset.all().order_by, "blah")

    def test_as_iterator(self):
        for index, value in enumerate(self.fieldset):
            self.assertEqual(index, value)

    def test_index_support(self):
        for i in range(0, 5):
            self.assertEqual(self.fieldset[i], i)

    def test_len_support(self):
        self.assertEqual(len(self.fieldset), 5)
