import pytest

from categories import semigroup, functor, bifunctor, applicative
from categories import sappend, fmap, first, second, bimap, apply
from categories.validation import Failure, Success, Validation
from categories.maybe import Just


class TestBasicMethods:
    def test_eq(self):
        assert Failure('cattywampus') == Failure('cattywampus')
        assert Success('cattywampus') == Success('cattywampus')
        assert not Failure('cattywampus') == Success('cattywampus')
        assert not Failure(17) == Failure(97)
        assert not Success(17) == Failure(97)
        assert not Success(17) == Success('cattywampus')
        assert not Success(17) == 17

    def test_repr(self):
        assert repr(Failure('cattywampus')) == "Failure('cattywampus')"
        assert repr(Success(42)) == "Success(42)"
        assert repr(Success(Just(42))) == "Success(Just(42))"

    def test_match(self):
        assert Success('catty').match(Success) is True
        assert Success(['wampus']).match(Failure) is False
        assert Failure(('higgledy', 'piggledy')).match(Failure) is True
        assert Failure(['argle', 'bargle']).match(Success) is False


class TestFunctor:
    def test_fmap_Success(self):
        x = Success(17)
        test = fmap(lambda a: a ** 2, x)
        assert test == Success(289)

    def test_fmap_Failure(self):
        assert fmap(lambda x: x ** 2, Failure(42)) == Failure(42)

    def test_functor_composition_law(self):
        f = lambda x: x * 7
        g = lambda y: y + 2
        x = Success(3)
        assert functor.composition_law(f, g, x)
        assert functor.identity_law(x)
        y = Failure(17)
        assert functor.composition_law(f, g, y)
        assert functor.identity_law(y)


class TestBifunctor:
    def test_first_left(self):
        x = Failure(17)
        test = first(lambda a: a ** 2, x)
        assert test == Failure(289)

    def test_first_rigth(self):
        assert first(lambda x: x ** 2, Success(42)) == Success(42)

    def test_second_left(self):
        assert second(lambda x: x ** 2, Failure(42)) == Failure(42)

    def test_second_right(self):
        x = Success(17)
        test = second(lambda a: a ** 2, x)
        assert test == Success(289)

    def test_bimap_left(self):
        f = lambda x: x + 2
        g = lambda x: x * 3
        test = bimap(f, g, Failure(2))
        assert test == Failure(4)

    def test_bimap_right(self):
        f = lambda x: x + 2
        g = lambda x: x * 3
        test = bimap(f, g, Success(2))
        assert test == Success(6)

    def test_bifunctor_composition_law(self):
        f = lambda x: x * 7
        g = lambda y: y + 2
        h = lambda x: x ** 2
        i = lambda y: y - 3
        x = Success(3)
        y = Failure(17)
        assert bifunctor.first_composition_law(f, g, x)
        assert bifunctor.first_identity_law(x)
        assert bifunctor.second_composition_law(f, g, x)
        assert bifunctor.second_identity_law(x)
        assert bifunctor.first_composition_law(f, g, y)
        assert bifunctor.first_identity_law(y)
        assert bifunctor.second_composition_law(f, g, y)
        assert bifunctor.second_identity_law(y)
        assert bifunctor.bimap_composition_law(f, g, h, i, x)
        assert bifunctor.bimap_composition_law(f, g, h, i, y)
        assert bifunctor.bifunctor_composition_law(f, g, x)
        assert bifunctor.bifunctor_composition_law(f, g, y)


class TestApplicative:
    def test_apply(self):
        assert apply(Success(lambda x: x * 2), Success(12)) == Success(24)
        assert apply(Success(lambda x: x * 2), Failure(12)) == Failure(12)
        assert apply(Failure("error message"),
                     Success(12)) == Failure("error message")
        assert apply(Failure("error message"),
                     Failure(12)) == Failure("error message")

    def test_applicative_id_law(self):
        assert applicative.identity_law(Success("test"))
        assert applicative.identity_law(Failure("test"))

    def test_applicative_homomorphism_law(self):
        f = lambda x: x.upper()
        x = 'test'
        assert applicative.homomorphism_law(f, x, Validation)

    def test_applicative_interchange_law(self):
        u = Success(lambda x: x + 3)
        y = 7
        assert applicative.interchange_law(u, y)
        v = Failure("error message")
        assert applicative.interchange_law(v, y)


class TestSemigroup:
    """
    Validation Semigroup acts on the inner type. Useful for
    accumulating exceptions on the Failure data constructor.
    """
    def test_semigroup_instance_sappend(self):
        semigroup.undefine_instance(list)
        semigroup.instance(list, lambda x, y: x + y)
        assert sappend(Failure([1]), Failure([2])) == Failure([1, 2])
        assert sappend(Success([1]), Success([2])) == Success([1, 2])
        assert sappend(Success([1]), Failure([2])) == Failure([2])
        assert sappend(Failure([1]), Success([2])) == Failure([1])
        semigroup.undefine_instance(list)
        with pytest.raises(TypeError):
            sappend(Failure([1]), Failure([2]))
