import unittest
import asyncio

from ...parsing import DictParser
from ...parsing.fields import StringField, DictField


def async_test(f):
    def wrapper(self):
        return asyncio.run(f(self))

    return wrapper


class TestParsing(unittest.TestCase):
    @async_test
    async def test_moo(self):
        # self.assertEqual(1, 1)
        class dp(DictParser):
            stringOne = StringField()
            stringTwo = StringField()
            dictOne = DictField(
                fields={
                    "stringThree": StringField(),
                    "stringFour": StringField(),
                    "dictTwo": DictField({}),
                }
            )

        parsed = await dp().parse({
            "stringOne": "moo",
            "stringTwo": "cow",
            "dictOne": {
                "stringThree": "moo",
                "stringFour": "cow",
                "dictTwo": {
                    "x": 1
                }
            }
        })

        self.assertEqual(parsed["stringOne"], "moo")
        self.assertEqual(parsed["stringTwo"], "cow")
        self.assertEqual(parsed["dictOne"]["stringThree"], "moo")
        self.assertEqual(parsed["dictOne"]["stringFour"], "cow")
        self.assertEqual(parsed["dictOne"]["dictTwo"]["x"], 1)


if __name__ == '__main__':
    unittest.main()