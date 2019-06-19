from unittest import TestCase

from perestroika.validators import AllowAll, DenyAll, AnyMatch, AllMatch


class ValidatorsTest(TestCase):
    def test_allow_all(self):
        validator = AllowAll()
        validator(1)
        validator('z')
        validator(None)

    def test_deny_all(self):
        validator = DenyAll()

        with self.assertRaises(TypeError):
            validator(1)

        with self.assertRaises(TypeError):
            validator('z')

        with self.assertRaises(TypeError):
            validator(None)

    def test_any_match(self):
        validator = AnyMatch(AllowAll(), DenyAll())
        validator(1)

        validator = AnyMatch(DenyAll(), AllowAll())
        validator(1)

    def test_all_match(self):
        validator = AllMatch(AllowAll(), DenyAll())

        with self.assertRaises(TypeError):
            validator(1)

        with self.assertRaises(TypeError):
            validator('z')

        with self.assertRaises(TypeError):
            validator(None)

        validator = AllMatch(DenyAll(), AllowAll())

        with self.assertRaises(TypeError):
            validator(1)

        with self.assertRaises(TypeError):
            validator('z')

        with self.assertRaises(TypeError):
            validator(None)

        validator = AllMatch(AllowAll(), AllowAll())
        validator(1)
        validator('z')
        validator(None)
