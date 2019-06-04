from ....test import test


class be:
    def __init__(self, expectInst):
        self._expectInst = expectInst
        self._actual = expectInst._actual

    @test
    def __call__(self, expected):
        actual = self._actual
        if actual is not expected:
            return f"expected {actual} to be {expected}"

    @test
    def anInstanceOf(self, expected):
        actual = self._actual

        if isinstance(actual, expected):
            return

        actualName = type(actual).__name__
        expectedName = expected.__name__
        return f"""\
            value is not an instance of {expectedName}"

            type of value: {actualName}
            """
