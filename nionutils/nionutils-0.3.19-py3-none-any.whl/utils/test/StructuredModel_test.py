# standard libraries
import collections
import contextlib
import copy
import unittest

# third party libraries

# local libraries
from nion.utils import StructuredModel


class TestStructuredModelClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_record_property(self):
        # test that a record gives access to a field value directly through a property on the record
        str_field = StructuredModel.define_field("s", StructuredModel.STRING, default="ss")
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertEqual("ss", model.s)

    def test_set_record_property(self):
        # test that a record gives can set a field value directly through a property on the record
        str_field = StructuredModel.define_field("s", StructuredModel.STRING, default="ss")
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertEqual("ss", model.s)
        model.s = "tt"
        self.assertEqual("tt", model.s)

    def test_set_record_property_fires_property_changed_event(self):
        str_field = StructuredModel.define_field("s", StructuredModel.STRING, default="ss")
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        was_property_changed_ref = [False]

        def handle_property_changed(name):
            self.assertEqual("s", name)
            was_property_changed_ref[0] = True

        with contextlib.closing(model.property_changed_event.listen(handle_property_changed)):
            self.assertFalse(was_property_changed_ref[0])
            model.s = "tt"
            self.assertTrue(was_property_changed_ref[0])

    def test_get_record_array_property(self):
        # test that a record gives access to a array value directly through a property on the record
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field)
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertIsInstance(model.a, collections.Sequence)

    def test_str_array_defaults(self):
        # test that an array of simple fields (str) can be initialized with default values
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertSequenceEqual(["a", "b", "c"],  model.a)

    def test_array_of_records_defaults(self):
        # test that an array of record fields can be initialized with default values
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        record = StructuredModel.define_record("A", [x_field, y_field])
        array_field = StructuredModel.define_array(record)
        str_field = StructuredModel.define_field("a", array_field, default=[{"x": 1, "y": 2}, {"x": 3, "y": 4}])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertEqual(2, len(model.a))
        self.assertEqual(1, model.a[0].x)
        self.assertEqual(4, model.a[1].y)

    def test_record_with_array_defaults(self):
        # test that a record with an array field can be initialized with default values
        array_field = StructuredModel.define_field("a", StructuredModel.define_array(StructuredModel.INT))
        record = StructuredModel.define_record("R", [array_field])
        record_field = StructuredModel.define_field("r", record, default={"a": [3, 4, 5]})
        schema = StructuredModel.define_record("Z", [record_field])
        model = StructuredModel.build_model(schema)
        self.assertEqual(3, len(model.r.a))
        self.assertEqual(4, model.r.a[1])
        self.assertEqual(5, model.r.a[2])

    def test_array_of_records_defaults_for_new_records(self):
        # test that building a model with defaults properly populates the defaults
        x_field = StructuredModel.define_field("x", StructuredModel.INT, default=1)
        y_field = StructuredModel.define_field("y", StructuredModel.INT, default=2)
        record = StructuredModel.define_record("A", [x_field, y_field])
        model = StructuredModel.build_model(record)
        self.assertEqual(1, model.x)
        self.assertEqual(2, model.y)

    def test_get_record_array_model(self):
        # test that a record gives access to a array model through a property on the record with _model suffix
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        self.assertIsInstance(model.a_model, StructuredModel.ArrayModel)

    def test_inserting_item_in_array_field_of_record_fires_item_inserted_event(self):
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        was_item_inserted_ref = [False]

        def handle_item_inserted(key, value, before_index):
            self.assertEqual("a", key)
            self.assertEqual("bb", value)
            self.assertEqual(1, before_index)
            was_item_inserted_ref[0] = True

        with contextlib.closing(model.item_inserted_event.listen(handle_item_inserted)):
            self.assertFalse(was_item_inserted_ref[0])
            model.a_model.insert_item(1, "bb")
            self.assertTrue(was_item_inserted_ref[0])

    def test_inserting_item_in_array_field_of_record_using_insert_fires_item_inserted_event(self):
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        was_item_inserted_ref = [False]

        def handle_item_inserted(key, value, before_index):
            self.assertEqual("a", key)
            self.assertEqual("bb", value)
            self.assertEqual(1, before_index)
            was_item_inserted_ref[0] = True

        with contextlib.closing(model.item_inserted_event.listen(handle_item_inserted)):
            self.assertFalse(was_item_inserted_ref[0])
            model.a.insert(1, "bb")
            self.assertTrue(was_item_inserted_ref[0])

    def test_removing_item_in_array_field_of_record_fires_item_removed_event(self):
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        was_item_removed_ref = [False]

        def handle_item_removed(key, value, before_index):
            self.assertEqual("a", key)
            self.assertEqual("b", value)
            self.assertEqual(1, before_index)
            was_item_removed_ref[0] = True

        with contextlib.closing(model.item_removed_event.listen(handle_item_removed)):
            self.assertFalse(was_item_removed_ref[0])
            model.a_model.remove_item(1)
            self.assertTrue(was_item_removed_ref[0])

    def test_removing_item_in_array_field_of_record_using_del_fires_item_removed_event(self):
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        was_item_removed_ref = [False]

        def handle_item_removed(key, value, before_index):
            self.assertEqual("a", key)
            self.assertEqual("b", value)
            self.assertEqual(1, before_index)
            was_item_removed_ref[0] = True

        with contextlib.closing(model.item_removed_event.listen(handle_item_removed)):
            self.assertFalse(was_item_removed_ref[0])
            del model.a[1]
            self.assertTrue(was_item_removed_ref[0])

    def test_setting_value_in_array_raises_exception(self):
        array_field = StructuredModel.define_array(StructuredModel.STRING)
        str_field = StructuredModel.define_field("a", array_field, default=["a", "b", "c"])
        schema = StructuredModel.define_record("R", [str_field])
        model = StructuredModel.build_model(schema)
        with self.assertRaises(IndexError):
            model.a[0] = "A"

    def test_copy_record_produces_copy(self):
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        schema = StructuredModel.define_record("A", [x_field, y_field])
        model = StructuredModel.build_model(schema, value={"x": 1, "y": 2})
        model_copy = copy.deepcopy(model)
        self.assertEqual(model.x, model_copy.x)
        self.assertEqual(model.y, model_copy.y)
        model.x = 4
        self.assertNotEqual(model.x, model_copy.x)
        self.assertEqual(model.y, model_copy.y)
        model.copy_from(model_copy)
        self.assertEqual(model.x, model_copy.x)
        self.assertEqual(model.y, model_copy.y)

    def test_copy_array_produces_copy(self):
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        record = StructuredModel.define_record("A", [x_field, y_field])
        schema = StructuredModel.define_array(record)
        model = StructuredModel.build_model(schema, value=[{"x": 1, "y": 2}, {"x": 3, "y": 4}])
        model_copy = copy.deepcopy(model)
        self.assertEqual(len(model.items), len(model_copy.items))
        self.assertEqual(model.items[1].x, model_copy.items[1].x)
        self.assertEqual(model.items[1].y, model_copy.items[1].y)
        model.items[1].x = 5
        self.assertNotEqual(model.items[1].x, model_copy.items[1].x)
        self.assertEqual(model.items[1].y, model_copy.items[1].y)
        model.copy_from(model_copy)
        self.assertEqual(len(model.items), len(model_copy.items))
        self.assertEqual(model.items[1].x, model_copy.items[1].x)
        self.assertEqual(model.items[1].y, model_copy.items[1].y)

    def test_change_array_basic_value_generates_model_changed(self):
        schema = StructuredModel.define_array(StructuredModel.STRING)
        model = StructuredModel.build_model(schema, value=["a", "b", "c"])
        changed_ref = [0]

        def property_changed():
            changed_ref[0] += 1

        with contextlib.closing(model.model_changed_event.listen(property_changed)):
            self.assertEqual(0, changed_ref[0])
            model.insert_item(1, "aa")
            self.assertEqual(1, changed_ref[0])
            model.remove_item(1)
            self.assertEqual(2, changed_ref[0])

    def test_change_array_records_value_generates_model_changed(self):
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        record = StructuredModel.define_record("A", [x_field, y_field])
        schema = StructuredModel.define_array(record)
        model = StructuredModel.build_model(schema, value=[{"x": 1, "y": 2}, {"x": 3, "y": 4}])
        changed_ref = [0]

        def property_changed():
            changed_ref[0] += 1

        with contextlib.closing(model.model_changed_event.listen(property_changed)):
            self.assertEqual(0, changed_ref[0])
            model.insert_item(1, StructuredModel.build_model(record, value={"x": 5, "y": 6}))
            self.assertEqual(1, changed_ref[0])
            model.items[1].x = 55
            self.assertEqual(2, changed_ref[0])

    def test_change_record_record_value_generates_model_changed(self):
        x_field = StructuredModel.define_field("x", StructuredModel.INT)
        y_field = StructuredModel.define_field("y", StructuredModel.INT)
        sub_record = StructuredModel.define_record("A", [x_field, y_field])
        sub_field = StructuredModel.define_field("a", sub_record)
        schema = StructuredModel.define_record("B", [sub_field])
        model = StructuredModel.build_model(schema, value={"a": {"x": 1, "y": 2}})
        changed_ref = [0]

        def property_changed():
            changed_ref[0] += 1

        with contextlib.closing(model.model_changed_event.listen(property_changed)):
            self.assertEqual(0, changed_ref[0])
            model.a.x = 11
            self.assertEqual(1, changed_ref[0])
