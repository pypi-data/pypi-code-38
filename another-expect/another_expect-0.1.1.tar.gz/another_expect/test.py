from ._vendor.tedent import tedent
from functools import wraps
from .ExpectFailedError import ExpectFailedError


def test(fn):
    @wraps(fn)
    def wrapTest(self, *args, **kwargs):
        if not hasattr(self, "_expectInst"):
            className = self.__class__.__name__
            raise ValueError(
                f"'_expectInst' doesn't exist on self for class {className}"
            )

        expectInst = self._expectInst

        if fn.__name__ == "__call__":
            expectInst._tests.append(fn.__class__.__name__)
        else:
            expectInst._tests.append(fn.__name__)

        maybeErrorMsg = fn(self, *args, **kwargs)

        if maybeErrorMsg:
            expectInst._expected = args[0]
            raise ExpectFailedError(tedent(f"\n{maybeErrorMsg}\n"), expectInst)

        return expectInst

    return wrapTest
