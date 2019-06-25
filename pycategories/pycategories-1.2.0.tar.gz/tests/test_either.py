from categories import applicative, apply, bind, fmap, functor
from categories import bifunctor, first, second, bimap
from categories import monad, mreturn
from categories.either import either, Either, Left, Right
from categories.maybe import Just


class TestBasicMethods:
    def test_eq(self):
        assert Left('cattywampus') == Left('cattywampus')
        assert Right('cattywampus') == Right('cattywampus')
        assert not Left('cattywampus') == Right('cattywampus')
        assert not Left(17) == Left(97)
        assert not Right(17) == Left(97)
        assert not Right(17) == Right('cattywampus')
        assert not Right(17) == 17

    def test_repr(self):
        assert repr(Left('cattywampus')) == "Left('cattywampus')"
        assert repr(Right(42)) == "Right(42)"
        assert repr(Right(Just(42))) == "Right(Just(42))"

    def test_match(self):
        assert Right('catty').match(Right) is True
        assert Right(['wampus']).match(Left) is False
        assert Left(('higgledy', 'piggledy')).match(Left) is True
        assert Left(['argle', 'bargle']).match(Right) is False


class TestFunctor:
    def test_fmap_right(self):
        x = Right(17)
        test = fmap(lambda a: a ** 2, x)
        assert test == Right(289)

    def test_fmap_left(self):
        assert fmap(lambda x: x ** 2, Left(42)) == Left(42)

    def test_functor_composition_law(self):
        f = lambda x: x * 7
        g = lambda y: y + 2
        x = Right(3)
        assert functor.composition_law(f, g, x)
        assert functor.identity_law(x)
        y = Left(17)
        assert functor.composition_law(f, g, y)
        assert functor.identity_law(y)


class TestBifunctor:
    def test_first_left(self):
        x = Left(17)
        test = first(lambda a: a ** 2, x)
        assert test == Left(289)

    def test_first_rigth(self):
        assert first(lambda x: x ** 2, Right(42)) == Right(42)

    def test_second_left(self):
        assert second(lambda x: x ** 2, Left(42)) == Left(42)

    def test_second_right(self):
        x = Right(17)
        test = second(lambda a: a ** 2, x)
        assert test == Right(289)

    def test_bimap_left(self):
        f = lambda x: x + 2
        g = lambda x: x * 3
        test = bimap(f, g, Left(2))
        assert test == Left(4)

    def test_bimap_right(self):
        f = lambda x: x + 2
        g = lambda x: x * 3
        test = bimap(f, g, Right(2))
        assert test == Right(6)

    def test_bifunctor_composition_law(self):
        f = lambda x: x * 7
        g = lambda y: y + 2
        h = lambda x: x ** 2
        i = lambda y: y - 3
        x = Right(3)
        y = Left(17)
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
        assert apply(Right(lambda x: x * 2), Right(12)) == Right(24)
        assert apply(Right(lambda x: x * 2), Left(12)) == Left(12)
        assert apply(Left("error message"), Right(12)) == Left("error message")
        assert apply(Left("error message"), Left(12)) == Left("error message")

    def test_applicative_id_law(self):
        assert applicative.identity_law(Right("test"))
        assert applicative.identity_law(Left("test"))

    def test_applicative_homomorphism_law(self):
        f = lambda x: x.upper()
        x = 'test'
        assert applicative.homomorphism_law(f, x, Either)

    def test_applicative_interchange_law(self):
        u = Right(lambda x: x + 3)
        y = 7
        assert applicative.interchange_law(u, y)
        v = Left("error message")
        assert applicative.interchange_law(v, y)


class TestMonad:
    def test_bind(self):
        f = lambda x: Right(x ** 2)
        assert bind(Right(13), f) == Right(169)
        assert bind(Left("error message"), f) == Left("error message")

    def test_mreturn(self):
        assert (mreturn("higgledy piggledy", Either) ==
                Right("higgledy piggledy"))

    def test_left_identity_law(self):
        a = "cattywampus"
        f = lambda x: Right(x + " and hoopajooped")
        assert monad.left_identity_law(a, f, Either)
        g = lambda x: Left(x + " and hoopajooped")
        assert monad.left_identity_law(a, g, Either)

    def test_right_identity_law(self):
        assert monad.right_identity_law(Right("a string"))
        assert monad.right_identity_law(Right([2, 3, 5, 7]))
        assert monad.right_identity_law(Left("a string"))
        assert monad.right_identity_law(Left([2, 3, 5, 7]))

    def test_associativity_law_right(self):
        m = Right(30)
        f = lambda x: Right(x / 3)
        g = lambda x: Right(x ** 2)
        h = lambda x: Right(x + 13)
        assert monad.associativity_law(m, f, g, h)

    def test_associativity_law_left(self):
        m = Left("error message")
        f = lambda x: Right(x / 3)
        g = lambda x: Right(x ** 2)
        h = lambda x: Right(x + 13)
        assert monad.associativity_law(m, f, g, h)


class TestEitherFunction:
    def test_left_case(self):
        f = lambda x: x.upper()
        g = lambda y: y ** 2
        assert either(f, g, Left("Some error")) == "SOME ERROR"

    def test_right_case(self):
        f = lambda x: x.upper()
        g = lambda y: y ** 2
        assert either(f, g, Right(23)) == 529
