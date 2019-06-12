
from j5basic import DictUtils
from j5test.Utils import raises
import datetime_tz
import pytz
import six

class TestUniqueItems(object):
    def test_unique_items(self):
        l = [9, 3, 4, 2, 4, 5, 3, 9]
        assert list(DictUtils.unique_items(l)) == [9, 3, 4, 2, 5]

class TestCIDict(object):
    def test_get(self):
        d = DictUtils.cidict()
        d["VaLuE"] = 5
        assert d["value"] == 5

    def test_retaincase(self):
        """tests that the key's original case is retained"""
        d = DictUtils.cidict()
        d["VaLuE"] = 5
        assert "VaLuE" in list(d.keys())
        assert "value" not in list(d.keys())

    def test_dict(self):
        """tests the normal dict functions, with thecidict peculiarities"""
        d = DictUtils.cidict({'VaLuE': 5})
        def setvalue(k, v):
            d[k] = v
        def delvalue(k):
            del d[k]
        def invalue(k):
            return k in d
        assert raises(TypeError, lambda: d[5])
        assert raises(IndexError, lambda: d['5'])
        assert raises(TypeError, setvalue, 5, 5)

        d['value'] = 6
        assert d['VaLuE'] == 6

        d.update(vaLue=7)
        assert d['VaLuE'] == 7
        d.update([('VALUE', 8)])
        assert d['VaLuE'] == 8
        d.update({'VAlue': 9})
        assert d['VaLuE'] == 9

        assert raises(TypeError, delvalue, 5)
        assert raises(IndexError, delvalue, '5')
        d['5'] = 5
        del d['5']
        assert d.get('5', None) is None

        assert raises(TypeError, invalue, 5)
        assert 'VALuE' in d
        assert d.has_key('vALUE')
        assert d.get('vaLUE') == 9

class TestAttrDict(object):
    def test_attrs(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        assert d["VaLuE"] == 5
        assert d.VaLuE == 5

    def test_attribify(self):
        nested = DictUtils.attribify([{"this": "is", "a": ["nested", {"dictionary": 4}]}])
        assert nested[0].this == "is"
        assert nested[0].a[0] == "nested"
        assert nested[0].a[1].dictionary == 4

    def test_missing_attr(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        assert "HeGeMoNy" not in list(d.keys())
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy", 9) == 9
        assert raises(AttributeError, getattr, d, "HeGeMoNy")

    def test_default_attr(self):
        d = DictUtils.attrdict()
        d["VaLuE"] = 5
        d.set_default_value(32)
        assert "HeGeMoNy" not in list(d.keys())
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy") == 32
        assert getattr(d, "HeGeMoNy", 9) == 32

class TestSetAttrDict(object):
    def test_set_attrs(self):
        """tests setting attributes both dict- and object-style"""
        d = DictUtils.setattrdict()
        d["VaLuE"] = 5
        assert d["VaLuE"] == 5
        assert d.VaLuE == 5
        d.ReDeeM = "price"
        assert d["ReDeeM"] == "price"
        assert d.ReDeeM == "price"

    def test_missing_attr(self):
        d = DictUtils.setattrdict()
        d.VaLuE = 5
        assert "HeGeMoNy" not in list(d.keys())
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy", 9) == 9
        assert raises(AttributeError, getattr, d, "HeGeMoNy")

    def test_default_attr(self):
        d = DictUtils.attrdict()
        d.VaLuE = 5
        d.set_default_value(32)
        assert "HeGeMoNy" not in list(d.keys())
        assert d.get("HeGeMoNy", 5) == 5
        assert raises(KeyError, d.__getitem__, "HeGeMoNy")
        assert getattr(d, "HeGeMoNy") == 32
        assert getattr(d, "HeGeMoNy", 9) == 32

class TestOrderedDict(object):
    def test_key_and_value_ordering(self):
        k = [5,1,2,3,7,6]
        v = ["a","b","c","d","e","f"]
        d = DictUtils.ordereddict(list(zip(k,v)))

        assert list(d.keys()) == k
        assert list(d.values()) == v
        assert list(d.items()) == list(zip(k,v))
        assert list(d.keys()) == k
        assert list(d.values()) == v
        assert list(d.items()) == list(zip(k,v))

    def test_setting(self):
        k = [5,1,2,3,7,6]
        v = ["a","b","c","d","e","f"]
        d = DictUtils.ordereddict(list(zip(k,v)))
        d.setdefault(8,"g")
        k.append(8)
        v.append("g")

        assert list(d.keys()) == k
        assert list(d.values()) == v
        assert list(d.items()) == list(zip(k,v))
        assert list(d.keys()) == k
        assert list(d.values()) == v
        assert list(d.items()) == list(zip(k,v))

    def test_dict(self):
        # Make an empty one
        cleand = DictUtils.ordereddict()

        # Make one from another
        k = [5,1,2,3,7,6]
        v = ["a","b","c","d","e","f"]
        d = DictUtils.ordereddict(DictUtils.ordereddict(list(zip(k,v))))
        def bad_dict():
            d = DictUtils.ordereddict(*k)

        d.setdefault(5,"g")
        assert d.get(5, None) == "a"
        d.update(t="g")
        assert d["t"] == "g"
        d.update([(7, "g")])
        assert d[7] == "g"
        d.update({8: "h"})
        assert d[8] == "h"
        assert raises(TypeError, bad_dict)

        del d[1]
        assert d.keys() == [5,2,3,7,6,"t",8]
        copyd = d.copy()

        assert list(copyd.keys()) == [5, 2, 3, 7, 6, "t", 8]
        assert list(copyd.values()) == ["a", "c", "d", "g", "f", "g", "h"]

        assert list(copyd.items())

        assert raises(KeyError, cleand.popitem)
        assert copyd.popitem() == (8, "h")
        assert copyd.pop(9, "default") == "default"
        assert copyd.pop(3) == "d"

        assert copyd.keys() == [5,2,7,6,"t"]
        copyd.clear()
        assert copyd.keys() == []

class TestDictHelpers(object):
    def test_assert_dicts_equal(self):
        d1 = {1:2, 3:4}
        d2 = {1:2, 3:4}
        d3 = {1:3, 3:5}
        d4 = {2:1, 4:3}

        DictUtils.assert_dicts_equal(d1, d2)
        DictUtils.assert_dicts_not_equal(d1, d3)
        DictUtils.assert_dicts_not_equal(d1, d4)

    def test_asset_dicts_equal_naive_datetimes(self):
        d1 = {1: datetime_tz.datetime_tz(2019,2,8,8,0,0, tzinfo=pytz.timezone('Africa/Johannesburg'))}
        d2 = {1: datetime_tz.datetime_tz(2019,2,8,6,0,0, tzinfo=pytz.utc)}

        DictUtils.assert_dicts_equal(d1, d2, True)

    def test_assert_dicts_not_equal(self):
        d1 = {1:2, 3:4}
        d2 = {1:2, 3:4}

        assert raises(AssertionError, DictUtils.assert_dicts_not_equal, d1, d2)

    def test_filterdict(self):
        d1 = {1:2, 3:4, 5:6, 7:8}

        DictUtils.assert_dicts_equal(DictUtils.filterdict(d1, {1,2,3}), {1:2, 3:4})

    def test_subtractdicts(self):
        d1 = {1:2, 3:4, 5:6, 7:8, 9:six.b("10"), 11:six.text_type("12")}
        d2 = {1:2, 3:5, 5: "6", 11: six.b("12"), 9: six.text_type("11")}

        DictUtils.assert_dicts_equal(DictUtils.subtractdicts(d1, d2), {3:4, 5:6, 7:8, 9: six.b("10")})

    def test_merge_dicts(self):
        d1 = {1:2, 3:4, 5:6, 7:8}
        d2 = {3:5, 7:9, 11:13}

        DictUtils.assert_dicts_equal(DictUtils.merge_dicts(d1, d2), {1:2, 3:5, 5:6, 7:9, 11:13})

    def test_mapdict(self):
        td = {1: 2, 3:4, 5:6}

        def keymap(x):
            return str(x)

        def valuemap(y):
            return y+1

        DictUtils.assert_dicts_equal(DictUtils.mapdict(td, None, None), td)
        DictUtils.assert_dicts_equal(DictUtils.mapdict(td, keymap, None), {"1": 2, "3": 4, "5": 6})
        DictUtils.assert_dicts_equal(DictUtils.mapdict(td, None, valuemap), {1: 3, 3: 5, 5: 7})
        DictUtils.assert_dicts_equal(DictUtils.mapdict(td, keymap, valuemap), {"1": 3, "3": 5, "5": 7})

    def test_upperkeys(self):
        td = {six.b("t"):1, six.text_type("u"): 2, None: 3}

        DictUtils.assert_dicts_equal(DictUtils.upperkeys(td), {six.b("T"): 1, six.text_type("U"): 2, None: 3})

