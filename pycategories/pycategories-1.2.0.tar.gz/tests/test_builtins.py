import pytest

from categories import applicative, apply
from categories import functor, fmap
from categories import mappend, mempty, monoid
from categories import bind, mreturn, monad
from categories import semigroup, sappend
from categories.maybe import Just, Nothing
from categories.utils import id_


class TestListSemigroup:
    def test_semigroup_associativity_law(self):
        x = [1, 2]
        y = [3, 4]
        z = [5, 6]
        assert semigroup.associativity_law(x, y, z)

    def test_sappend(self):
        x = [1, 2]
        y = [3, 4]
        assert sappend(x, y) == [1, 2, 3, 4]


class TestListMonoid:
    def test_monoid_associativity_law(self):
        x = [1, 2]
        y = [3, 4]
        z = [5, 6]
        assert monoid.associativity_law(x, y, z)

    def test_monoid_law(self):
        assert monoid.identity_law([1, 2])

    def test_mappend(self):
        x = [1, 2]
        y = [3, 4]
        assert mappend(x, y) == [1, 2, 3, 4]

    def test_doesnt_mutate_mempty(self):
        mempty(list).append('test')
        assert mempty(list) == []


class TestListFunctor:
    def test_fmap(self):
        assert fmap(lambda x: x.upper(), ["ab", "cd"]) == ["AB", "CD"]

    def test_functor_id_law(self):
        assert functor.identity_law([1, 2])

    def test_functor_composition_law(self):
        f = lambda x: x * 2
        g = lambda x: x + 3
        x = [1, 2, 3, 4]
        assert functor.composition_law(f, g, x)


class TestListApplicative:
    def test_apply(self):
        f = lambda x: x + 1
        g = lambda x: x * 2
        h = lambda x: x ** 2
        expected = [3, 4, 6, 4, 6, 10, 4, 9, 25]
        assert apply([f, g, h], [2, 3, 5]) == expected

    def test_applicative_id_law(self):
        assert applicative.identity_law(['ab', 'cd', 'ef'])

    def test_applicative_homomorphism_law(self):
        f = lambda x: x * 3
        x = 2
        assert applicative.homomorphism_law(f, x, list)

    def test_applicative_interchange_law(self):
        u = [lambda x: x + 3]
        y = 7
        assert applicative.interchange_law(u, y)


class TestListMonad:
    def test_bind(self):
        xs = [2, 3, 5, 7]
        f = lambda x: [x ** 2]
        assert bind(xs, f) == [4, 9, 25, 49]

    def test_mreturn(self):
        assert mreturn(Just(18), list) == [Just(18)]

    def test_left_identity_law(self):
        a = "test"
        f = lambda x: [x.upper()]
        assert monad.left_identity_law(a, f, list)

    def test_right_identity_law(self):
        m = [Just(3)]
        assert monad.right_identity_law(m)

    def test_associativity_law(self):
        m = [2, 3, 5]
        f = lambda x: [x + 3]
        g = lambda x: [x * 2]
        assert monad.associativity_law(m, f, g)


class TestStringSemigroup:
    def test_semigroup_associativity_law(self):
        x = "catty"
        y = "wamp"
        z = "us"
        assert semigroup.associativity_law(x, y, z)

    def test_sappend(self):
        x = "catty"
        y = "wampus"
        assert sappend(x, y) == "cattywampus"


class TestStringMonoid:
    def test_monoid_associativity_law(self):
        x = "catty"
        y = "wamp"
        z = "us"
        assert monoid.associativity_law(x, y, z)

    def test_monoid_law(self):
        assert monoid.identity_law("cattywampus")

    def test_monoid(self):
        x = "catty"
        y = "wampus"
        assert mappend(x, y) == "cattywampus"


class TestStringFunctor:
    def test_fmap(self):
        assert fmap(lambda x: x.upper() * 2, "wampus") == "WWAAMMPPUUSS"

    def test_functor_id_law(self):
        assert functor.identity_law("cattywampus")

    def test_functor_composition_law(self):
        f = lambda x: chr(ord(x) + 2)
        g = lambda x: x + 'Q'
        x = "cattywampus"
        assert functor.composition_law(f, g, x)


class TestTupleSemigroup:
    def test_sappend(self):
        a = (Just("x"), Just("yz"))
        b = (Just("ab"), Nothing())
        expected = (Just("xab"), Just("yz"))
        assert sappend(a, b) == expected
        assert sappend(a, ()) == a
        assert sappend((), b) == b

    def test_error_on_mismatched_length(self):
        with pytest.raises(TypeError) as exc:
            sappend(("a", "b"), ("a", "b", "c"))
        assert "must have the same length" in str(exc.value)

    def test_semigroup_associativity_law(self):
        x = ("ab", "cd")
        y = ("ef", "ghi")
        z = ("jkl", "mnop")
        assert semigroup.associativity_law(x, y, z)


class TestTupleMonoid:
    def test_mappend(self):
        a = (Just("x"), Just("yz"))
        b = (Just("ab"), Nothing())
        expected = (Just("xab"), Just("yz"))
        assert mappend(a, b) == expected
        assert mappend(a, ()) == a
        assert mappend((), b) == b

    def test_error_on_mismatched_length(self):
        with pytest.raises(TypeError) as exc:
            mappend(("a", "b"), ("a", "b", "c"))
        assert "must have the same length" in str(exc.value)

    def test_monoid_associativity_law(self):
        x = ("ab", "cd")
        y = ("ef", "ghi")
        z = ("jkl", "mnop")
        assert monoid.associativity_law(x, y, z)

    def test_monoid_law(self):
        assert monoid.identity_law(("a", "bc", "def"))


class TestTupleFunctor:
    def test_fmap(self):
        x = (Just("a string"), 12)
        assert fmap(lambda x: x ** 2, x) == (Just("a string"), 144)

    def test_fmap_wrong_length(self):
        with pytest.raises(TypeError) as exc:
            fmap(id_, (1, 2, 3))
        assert "only defined for 2-tuples" in str(exc.value)

    def test_functor_id_law(self):
        assert functor.identity_law((Just("a"), Nothing()))

    def test_functor_composition_law(self):
        f = lambda x: x * 2
        g = lambda x: x + 3
        x = (11, 13)
        assert functor.composition_law(f, g, x)


class TestTupleApplicative:
    def test_apply(self):
        fs = ("added 13 to ", lambda x: x + 13)
        xs = ("27", 27)
        assert apply(fs, xs) == ("added 13 to 27", 40)

    def test_apply_wrong_length(self):
        with pytest.raises(TypeError) as exc:
            apply(("abc", id_), (1, 2, 3))
        assert "only defined for 2-tuples" in str(exc.value)

    def test_applicative_id_law(self):
        assert applicative.identity_law(('ab', 'cd'), type_form=str)

    def test_applicative_homomorphism_law(self):
        f = lambda x: x * 3
        x = 18
        assert applicative.homomorphism_law(f, x, tuple, str)

    def test_applicative_interchange_law(self):
        u = ('string', lambda x: x + 3)
        y = 7
        assert applicative.interchange_law(u, y, str)


class TestTupleMonad:
    def test_bind(self):
        a = ("started with 17.", 17)
        b = lambda x: (" then added 4.", x + 4)
        assert bind(a, b) == ("started with 17. then added 4.", 21)

    def test_left_identity_law(self):
        a = "test"
        f = lambda x: ("uppercase", x.upper())
        assert monad.left_identity_law(a, f, tuple, type_form=str)

    def test_right_identity_law(self):
        m = ("example", Just(18))
        assert monad.right_identity_law(m, type_form=str)

    def test_associativity_law(self):
        m = ("started with 10.", 10)
        f = lambda x: (" added 3.", x + 3)
        g = lambda x: (" multiplied by 2.", x * 2)
        assert monad.associativity_law(m, f, g)
