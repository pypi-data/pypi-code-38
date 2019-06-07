from handympi import foreach, MY_RANK

class BasicTests:

    def test_foreach(self):

        x = foreach(lambda x: x**3, list(range(40)))
        y = sum(map(lambda x: x**3, range(40)))

        assert x == y

