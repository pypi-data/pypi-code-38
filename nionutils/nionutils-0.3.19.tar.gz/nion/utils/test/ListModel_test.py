# standard libraries
import contextlib
import logging
import unittest

# third party libraries
# None

# local libraries
from nion.utils import ListModel
from nion.utils import Observable


class A:
    def __init__(self, s: str):
        self.s = s


class B:
    def __init__(self, a: A):
        self.s = a.s + "_B"


class TestListModelClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_initial_mapped_model_values_are_correct(self):
        l = ListModel.ListModel("items")
        l.append_item(A("1"))
        l.append_item(A("2"))
        l2 = ListModel.MappedListModel(container=l, master_items_key="items", items_key="itemsb", map_fn=B)
        self.assertEqual([b.s for b in map(B, l.items)], [b.s for b in l2.items])
        self.assertEqual(l2.itemsb, l2.items)
        self.assertEqual("2_B", l2.items[1].s)

    def test_mapped_model_values_after_insert_are_correct(self):
        l = ListModel.ListModel("items")
        l.append_item(A("1"))
        l.append_item(A("2"))
        l2 = ListModel.MappedListModel(container=l, master_items_key="items", items_key="itemsb", map_fn=B)
        l.insert_item(1, A("1.5"))
        self.assertEqual([b.s for b in map(B, l.items)], [b.s for b in l2.items])
        self.assertEqual(l2.itemsb, l2.items)
        self.assertEqual("1.5_B", l2.items[1].s)

    def test_mapped_model_values_after_delete_are_correct(self):
        l = ListModel.ListModel("items")
        l.append_item(A("1"))
        l.append_item(A("2"))
        l.append_item(A("3"))
        l2 = ListModel.MappedListModel(container=l, master_items_key="items", items_key="itemsb", map_fn=B)
        l.remove_item(1)
        self.assertEqual([b.s for b in map(B, l.items)], [b.s for b in l2.items])
        self.assertEqual(l2.itemsb, l2.items)
        self.assertEqual("3_B", l2.items[1].s)

    def test_mapped_model_selection_after_insert_are_correct(self):
        l = ListModel.ListModel("items")
        l.append_item(A("1"))
        l.append_item(A("2"))
        l2 = ListModel.MappedListModel(container=l, master_items_key="items", items_key="itemsb", map_fn=B)
        s = l2.make_selection()
        s.add(0)
        s.add(1)
        l.insert_item(1, A("1.5"))
        self.assertEqual({0, 2}, s.indexes)

    def test_mapped_model_selection_after_delete_are_correct(self):
        l = ListModel.ListModel("items")
        l.append_item(A("1"))
        l.append_item(A("2"))
        l.append_item(A("3"))
        l2 = ListModel.MappedListModel(container=l, master_items_key="items", items_key="itemsb", map_fn=B)
        s = l2.make_selection()
        s.add(0)
        s.add(2)
        l.remove_item(1)
        self.assertEqual({0, 1}, s.indexes)

    def test_flattened_model_initializes_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs1.append_item("12")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        bs3.append_item("32")
        bs3.append_item("33")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        self.assertEqual(["11", "12", "31", "32", "33"], f.cs)

    def test_flattened_model_inserts_master_item_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs1.append_item("12")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        bs3.append_item("32")
        bs3.append_item("33")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        bs4 = ListModel.ListModel("bs")
        bs4.append_item("41")
        bs4.append_item("42")
        l.insert_item(1, bs4)
        self.assertEqual(["11", "12", "41", "42", "31", "32", "33"], f.cs)

    def test_flattened_model_removes_master_item_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs1.append_item("12")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        bs3.append_item("32")
        bs3.append_item("33")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        l.remove_item(0)
        self.assertEqual(["31", "32", "33"], f.cs)

    def test_flattened_model_inserts_child_item_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs1.append_item("12")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        bs3.append_item("32")
        bs3.append_item("33")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        bs1.insert_item(1, "115")
        self.assertEqual(["11", "115", "12", "31", "32", "33"], f.cs)

    def test_flattened_model_removes_child_item_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs1.append_item("12")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        bs3.append_item("32")
        bs3.append_item("33")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        bs1.remove_item(1)
        self.assertEqual(["11", "31", "32", "33"], f.cs)

    def test_flattened_model_with_empty_master_item_closes_properly(self):
        l = ListModel.ListModel("as")
        bs1 = ListModel.ListModel("bs")
        bs1.append_item("11")
        bs2 = ListModel.ListModel("bs")
        bs3 = ListModel.ListModel("bs")
        bs3.append_item("31")
        l.append_item(bs1)
        l.append_item(bs2)
        l.append_item(bs3)
        f = ListModel.FlattenedListModel(container=l, master_items_key="as", child_items_key="bs", items_key="cs")
        with contextlib.closing(f):
            pass


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
