import unittest

from ..dto import DTO
from ..dto import ImmutableDTO


class DataTransferObjectTestCase(unittest.TestCase):
    dto_class = DTO

    def test_from_dict_recursive(self):
        mapping = {
            'foo': {'bar': 1}
        }
        dto = self.dto_class.fromdict(mapping)
        self.assertIsInstance(dto, self.dto_class)
        self.assertIsInstance(dto['foo'], self.dto_class)

    def test_serialize_returns_dict(self):
        d1 = self.dto_class(foo=1)
        self.assertIsInstance(d1.__serialize__(lambda x: x), dict)

    def test_as_dict_nested_dto(self):
        d1 = self.dto_class(
            foo=self.dto_class(bar=1)
        )
        d2 = d1.as_dict()
        self.assertIsInstance(d2['foo'], dict)

    def test_as_dict_nested_dict(self):
        d1 = self.dto_class(
            foo=dict(bar=1)
        )
        d2 = d1.as_dto()
        self.assertIsInstance(d2['foo'], self.dto_class)

    def test_as_dto_with_dto_recurse(self):
        d1 = self.dto_class(
            foo=dict(
                bar=self.dto_class(baz=1)
            )
        )
        d2 = d1.as_dto(with_dto=True)
        self.assertIsInstance(d2.foo.bar, self.dto_class)

    def test_list_of_dicts_to_dtos(self):
        d1 = self.dto_class(
            foo=[
                {'bar': 1},
                {'baz': 2}
            ])
        d2 = d1.as_dto()
        self.assertIsInstance(d2.foo[0], self.dto_class)
        self.assertIsInstance(d2.foo[1], self.dto_class)

    def test_setattr(self):
        if self.dto_class.__immutable__:
            raise unittest.SkipTest("No setter test on immutable.")
        d1 = self.dto_class(foo=1)
        d1.foo = 2
        self.assertEqual(d1.foo, 2)

    def test_getattr_raises_on_nonexisting(self):
        d1 = self.dto_class(foo=1)
        with self.assertRaises(AttributeError):
            d1.bar

    def test_intersect_union(self):
        d1 = self.dto_class(foo=1)
        d2 = self.dto_class(foo=1, bar=2)
        self.assertEqual(set((d1 & d2).keys()), set(['foo']))

    def test_intersect_with_set(self):
        d1 = self.dto_class(foo=1)
        d2 = d1 & ['foo']
        self.assertEqual(set((d1 & d2).keys()), set(['foo']))

    def test_intersect_takes_right_operand_values(self):
        d1 = self.dto_class(foo=1)
        d2 = self.dto_class(foo=2, bar=2)
        d3 = d1 & d2
        self.assertEqual(d3.foo, 2)

    def test_union_non_dict_raises_valuerror(self):
        d1 = self.dto_class(foo=1)
        with self.assertRaises(ValueError):
            d1 | ['foo']

    def test_union_takes_values_from_right_operand(self):
        d1 = self.dto_class(foo=1)
        d2 = self.dto_class(foo=2, bar=3)
        d3 = d1 | d2
        self.assertEqual(d2.foo, 2)

    def test_union_takes_all_keys(self):
        d1 = self.dto_class(foo=1)
        d2 = self.dto_class(foo=2, bar=3)
        d3 = d1 | d2
        self.assertEqual(set(d3.keys()), set(['foo','bar']))

    def test_sub(self):
        d1 = self.dto_class(foo=1, bar=2)
        d2 = d1 - ['bar']
        self.assertEqual(set(d2.keys()), set(['foo']))

    def test_sub_raises_with_non_list(self):
        d1 = self.dto_class(foo=1, bar=2)
        with self.assertRaises(TypeError):
            d1 - 'foo'

class ImmutableDataTransferObjectTestCase(DataTransferObjectTestCase):
    dto_class = ImmutableDTO

    def test_setattr(self):
        if not self.dto_class.__immutable__:
            raise unittest.SkipTest("No setter test on non-immutable.")
        d1 = ImmutableDTO(foo=1)
        with self.assertRaises(TypeError):
            d1.foo = 2
