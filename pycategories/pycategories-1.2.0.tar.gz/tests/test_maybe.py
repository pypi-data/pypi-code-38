import pytest

from categories import applicative, apply, bind, fmap, functor
from categories import mappend, monad, monoid, mreturn
from categories.maybe import Just, Maybe, maybe, Nothing
from categories import semigroup, sappend


class TestBasicMethods:
    def test_just_eq(self):
        assert Just('abc') != Just('xyz')
        assert Just([1, 2, 3]) == Just([1, 2, 3])
        assert Just(17) != 17
        assert Just('x') != Nothing()

    def test_nothing_eq(self):
        assert Nothing() == Nothing()
        assert Nothing() != 42
        assert Nothing() is not None

    def test_repr_just(self):
        assert repr(Just(17)) == 'Just(17)'
        assert repr(Just('a string')) == "Just('a string')"

    def test_repr_nothing(self):
        assert repr(Nothing()) == 'Nothing'

    def test_match(self):
        assert Just(17).match(Just) is True
        assert Just(['xyz']).match(Nothing) is False
        assert Nothing().match(Nothing) is True
        assert Nothing().match(Just) is False


class TestSemigroup:
    def test_sappend(self):
        x = Just([1, 2])
        y = Just([3, 4])
        assert sappend(x, y) == Just([1, 2, 3, 4])
        assert sappend(x, Nothing()) == x
        assert sappend(Nothing(), y) == y
        assert sappend(Nothing(), Nothing()) == Nothing()

    def test_semigroup_associativity_law(self):
        x = Just([2, 3])
        y = Just([4, 5])
        z = Just([12, 24])
        assert semigroup.associativity_law(x, y, z)


class TestMonoid:
    def test_mappend(self):
        x = Just([1, 2])
        y = Just([3, 4])
        assert mappend(x, y) == Just([1, 2, 3, 4])
        assert mappend(x, Nothing()) == x
        assert mappend(Nothing(), y) == y
        assert mappend(Nothing(), Nothing()) == Nothing()

    def test_monoid_laws(self):
        x = Just([2, 3])
        y = Just([4, 5])
        z = Just([12, 24])
        assert monoid.associativity_law(x, y, z)
        assert monoid.identity_law(x)


class TestFunctor:
    def test_fmap_just(self):
        x = Just(17)
        test = fmap(lambda a: a ** 2, x)
        assert test == Just(289)

    def test_fmap_nothing(self):
        assert fmap(lambda x: x ** 2, Nothing()) == Nothing()

    def test_functor_composition_law(self):
        f = lambda x: x * 7
        g = lambda y: y + 2
        x = Just(3)
        assert functor.composition_law(f, g, x)
        assert functor.identity_law(x)


class TestApplicative:
    def test_apply(self):
        assert apply(Just(lambda x: x * 2), Just(12)) == Just(24)
        assert apply(Just(lambda x: x * 2), Nothing()) == Nothing()

    def test_applicative_id_law(self):
        assert applicative.identity_law(Just("test"))

    def test_applicative_homomorphism_law(self):
        f = lambda x: x.upper()
        x = 'test'
        assert applicative.homomorphism_law(f, x, Maybe)

    def test_applicative_interchange_law(self):
        u = Just(lambda x: x + 3)
        y = 7
        assert applicative.interchange_law(u, y)

    @pytest.mark.skip("Problems with applicative_composition_law function")
    def test_applicative_composition_law(self):
        u = Just(lambda x: x * 10)
        v = Just(lambda x: x + 13)
        w = Just(7)
        assert applicative.composition_law(u, v, w)


class TestMonad:
    def test_bind(self):
        f = lambda x: Just(x ** 2)
        assert bind(Just(13), f) == Just(169)
        assert bind(Nothing(), f) == Nothing()

    def test_mreturn(self):
        assert mreturn("higgledy piggledy", Maybe) == Just("higgledy piggledy")

    def test_left_identity_law(self):
        a = "cattywampus"
        f = lambda x: Just(x + " and hoopajooped")
        assert monad.left_identity_law(a, f, Maybe)

    def test_right_identity_law(self):
        assert monad.right_identity_law(Just("in case"))
        assert monad.right_identity_law(Just([2, 3, 5, 7]))

    def test_associativity_law(self):
        m = Just(30)
        f = lambda x: Just(x / 3)
        g = lambda x: Just(x ** 2)
        h = lambda x: Just(x + 13)
        assert monad.associativity_law(m, f, g, h)


class TestMaybeFunction:
    def test_nothing_case(self):
        f = lambda x: x * 10
        assert maybe(0, f, Nothing()) == 0

    def test_just_case(self):
        f = lambda x: x * 10
        assert maybe(0, f, Just(18)) == 180
