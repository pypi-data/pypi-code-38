# standard libraries
import logging
import unittest

# third party libraries
# None

# local libraries
from nion.utils import Binding
from nion.utils import Event
from nion.utils import ListModel


class TupleModel:

    def __init__(self):
        self.__tuple = None
        self.property_changed_event = Event.Event()

    @property
    def tuple(self):
        return self.__tuple

    @tuple.setter
    def tuple(self, value):
        self.__tuple = value
        self.property_changed_event.fire("tuple")


class TestBindingClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_should_be_able_to_get_items_from_list_binding(self):
        list_model = ListModel.ListModel("items")
        list_model.insert_item(0, "zero")
        list_model.insert_item(1, "one")
        list_model.insert_item(2, "two")
        binding = Binding.ListBinding(list_model, "items")
        items = binding.items
        self.assertEqual(len(items), 3)
        self.assertEqual(items[2], "two")
        list_model.insert_item(0, "negative")
        self.assertEqual(len(items), 4)
        self.assertEqual(items[3], "two")

    def test_inserting_and_removing_item_into_binding_notifies_target(self):
        list_model = ListModel.ListModel("items")
        binding = Binding.ListBinding(list_model, "items")
        list_copy = list()

        def inserter(value: str, index: int) -> None:
            list_copy.insert(index, value)

        def remover(index: int) -> None:
            del list_copy[index]

        binding.inserter = inserter
        binding.remover = remover
        list_model.insert_item(0, "zero")
        list_model.insert_item(1, "one")
        self.assertEqual(len(list_copy), 2)
        self.assertEqual(list_copy[1], "one")
        list_model.remove_item(0)
        self.assertEqual(len(list_copy), 1)
        self.assertEqual(list_copy[0], "one")

    def test_tuple_binding_pads_to_index_if_necessary(self):
        # this allows the source to more easily go from None to a partialy tuple None -> (3, None) -> (3, 4)
        source = TupleModel()
        self.assertEqual(None, source.tuple)
        binding0 = Binding.TuplePropertyBinding(source, "tuple", 0)
        binding2 = Binding.TuplePropertyBinding(source, "tuple", 2)
        binding0.update_source("abc")
        self.assertEqual(("abc", ), source.tuple)
        binding2.update_source("ghi")
        self.assertEqual(("abc", None, "ghi"), source.tuple)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
