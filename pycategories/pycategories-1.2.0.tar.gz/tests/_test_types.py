from categories import fp, bind
from categories.maybe import Just, Maybe
from categories.either import Either, Right, Left


def plus1(x: int) -> int:
    return x + 1


# Maybe

# correct
mInt1: Maybe[int] = Just(1)  # should pass
mInt3: Maybe[int] = mInt1 | bind | (lambda x: Just(x + 1))  # should pass
mInt4: Maybe[int] = plus1 | fp | mInt1  # should pass
int0: Maybe[int] = 1  # should NOT pass
str0: Maybe[str] = Just(1)  # should NOT pass

# failing
mInt2: Maybe[int] = mInt1 | bind | plus1  # should NOT pass


# Either

# correct
eInt1: Either[str, int] = Right(1)  # should pass
eStr1: Either[str, int] = Left('a')  # should pass
eInt2: Either[str, int] = Right('a')  # should NOT pass
eStr2: Either[str, int] = Left(1)  # should NOT pass
eInt4: Either[str, int] = plus1 | fp | eInt1  # should pass
eStr4: Either[str, int] = plus1 | fp | eInt1  # should pass

# failing
eInt3: Either[str, int] = eInt1 | bind | plus1  # should NOT pass
eStr3: Either[str, int] = eStr1 | bind | plus1  # should NOT pass


# Type mismatch

# correct
meInt1: Either[str, int] = Just(1)  # should NOT pass

# failing
meInt12: Either[str, int] = plus1 | fp | Just(1)  # should NOT pass
