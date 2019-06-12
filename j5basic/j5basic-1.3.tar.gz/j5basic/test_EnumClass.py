#!/usr/bin/env python

from j5basic import EnumClass
from j5test import Utils

class MyEnum(EnumClass.enum):
    APPLES = 1
    ORANGES = 2

class MyStringEnum(EnumClass.enum):
    __constant_class__ = str
    NEW_YORK = "Big Apple"
    ORANGE_RIVER = "A Rafting Opportunity"

class TestEnum(object):
    """Tests creating and using EnumClass.enum objects"""
    def test_create(self):
        """Tests the creation of enums, and that values can be looked up"""
        assert MyEnum.APPLES == 1
        assert MyEnum.ORANGES == 2
        assert MyEnum.get_name() == "MyEnum"

    def test_identify(self):
        """Tests finding the names mapped to constants (and failure to find)"""
        assert MyEnum.identify(1) == "APPLES"
        assert MyEnum.identify(2) == "ORANGES"
        assert Utils.raises(KeyError, MyEnum.identify, 3)
        assert MyEnum.identify(3, "MONKEY") == "MONKEY"

    def test_lookup(self):
        """Tests looking up an enum by name"""
        assert MyEnum.lookup("APPLES") == 1
        assert MyEnum.lookup("ORANGES") == 2
        assert Utils.raises(KeyError, MyEnum.lookup, "PEARS")
        assert MyEnum.lookup("PEARS", 4) == 4

    def test_iter(self):
        """Tests that you can iterate over constants"""
        assert list(iter(MyEnum)) == [1, 2]

class TestStringEnum(object):
    """Tests creating and using EnumClass.enum objects with string values"""
    def test_create(self):
        """Tests the creation of enums, and that values can be looked up"""
        assert MyStringEnum.NEW_YORK == "Big Apple"
        assert MyStringEnum.ORANGE_RIVER == "A Rafting Opportunity"
        assert MyStringEnum.get_name() == "MyStringEnum"

    def test_identify(self):
        """Tests finding the names mapped to constants (and failure to find)"""
        assert MyStringEnum.identify("Big Apple") == "NEW_YORK"
        assert MyStringEnum.identify("A Rafting Opportunity") == "ORANGE_RIVER"
        assert Utils.raises(KeyError, MyStringEnum.identify, 1)
        assert Utils.raises(KeyError, MyStringEnum.identify, "new_york")
        assert MyStringEnum.identify("Quartzitic Sandstone", "TABLE_MOUNTAIN") == "TABLE_MOUNTAIN"

    def test_lookup(self):
        """Tests looking up an enum by name"""
        assert MyStringEnum.lookup("NEW_YORK") == "Big Apple"
        assert MyStringEnum.lookup("ORANGE_RIVER") == "A Rafting Opportunity"
        assert Utils.raises(KeyError, MyStringEnum.lookup, "TABLE_MOUNTAIN")
        assert MyStringEnum.lookup("TABLE_MOUNTAIN", "Quartzitic Sandstone") == "Quartzitic Sandstone"

    def test_iter(self):
        """Tests that you can iterate over constants"""
        # TODO: iterate in definition order rather than constant order
        assert list(iter(MyStringEnum)) == ["A Rafting Opportunity", "Big Apple"]

