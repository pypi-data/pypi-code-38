import unittest

from status import Failed, InProgress, NotStarted, Status, Succeeded


class StatusTests(unittest.TestCase):
    def test_init(self):
        with self.assertRaises(NotImplementedError) as e:
            Status()
        self.assertEqual(
            str(e.exception),
            "Please instantiate one of the `Status` subclasses:\n"
            "\n\t- `Failed`"
            "\n\t- `NotStarted`"
            "\n\t- `InProgress(progress)`"
            "\n\t- `Succeeded`",
        )

        self.assertIs(type(Failed()), Failed)
        self.assertIs(type(NotStarted()), NotStarted)
        self.assertIs(type(InProgress()), InProgress)
        self.assertIs(type(Succeeded()), Succeeded)

        self.assertEqual(Failed().progress, None)
        self.assertEqual(InProgress(0).progress, 0)
        self.assertEqual(InProgress(7).progress, 7)
        self.assertEqual(InProgress(100).progress, 100)
        self.assertEqual(NotStarted().progress, None)
        self.assertEqual(Succeeded().progress, None)

    def test_repr(self):
        self.assertEqual(repr(Failed()), "Failed()")
        self.assertEqual(repr(NotStarted()), "NotStarted()")
        self.assertEqual(repr(InProgress()), "InProgress(0)")
        self.assertEqual(repr(InProgress(5)), "InProgress(5)")
        self.assertEqual(repr(InProgress(-100)), "InProgress(0)")
        self.assertEqual(repr(InProgress(234)), "InProgress(100)")
        self.assertEqual(repr(Succeeded()), "Succeeded()")

    def test_eq(self):
        self.assertEqual(Failed(), Failed())
        self.assertEqual(NotStarted(), NotStarted())
        self.assertEqual(InProgress(), InProgress())
        self.assertEqual(InProgress(55.7), InProgress(55.7))
        self.assertEqual(InProgress(44 / 57), InProgress(44 / 57))
        self.assertEqual(InProgress(), InProgress(0))
        self.assertEqual(InProgress(-34), InProgress(0))
        self.assertEqual(InProgress(120428), InProgress(100))
        self.assertEqual(InProgress(12313120428 / 2343), InProgress(100))
        self.assertEqual(Succeeded(), Succeeded())

        self.assertNotEqual(Failed(), NotStarted())
        self.assertNotEqual(Failed(), InProgress())
        self.assertNotEqual(Failed(), Succeeded())
        self.assertNotEqual(NotStarted(), InProgress(34))
        self.assertNotEqual(NotStarted(), Succeeded())
        self.assertNotEqual(InProgress(34), Succeeded())
        self.assertNotEqual(InProgress(5), InProgress(55))

    def test_lt(self):
        self.assertFalse(Failed() < Failed())
        self.assertFalse(NotStarted() < NotStarted())
        self.assertFalse(InProgress() < InProgress())
        self.assertFalse(InProgress(5) < InProgress(5))
        self.assertFalse(Succeeded() < Succeeded())

        self.assertLess(Failed(), NotStarted())
        self.assertLess(Failed(), InProgress(0))
        self.assertLess(Failed(), InProgress(100))
        self.assertLess(Failed(), Succeeded())
        self.assertLess(NotStarted(), InProgress())
        self.assertLess(NotStarted(), Succeeded())
        self.assertLess(InProgress(5), InProgress(6))
        self.assertLess(InProgress(100), Succeeded())

    def test_lte(self):
        self.assertLessEqual(Failed(), Failed())
        self.assertLessEqual(NotStarted(), NotStarted())
        self.assertLessEqual(InProgress(), InProgress())
        self.assertLessEqual(InProgress(5), InProgress(5))
        self.assertLessEqual(Succeeded(), Succeeded())
        self.assertLessEqual(Failed(), NotStarted())
        self.assertLessEqual(Failed(), InProgress(0))
        self.assertLessEqual(Failed(), InProgress(100))
        self.assertLessEqual(Failed(), Succeeded())
        self.assertLessEqual(NotStarted(), InProgress())
        self.assertLessEqual(NotStarted(), Succeeded())
        self.assertLessEqual(InProgress(5), InProgress(6))
        self.assertLessEqual(InProgress(100), Succeeded())

    def test_gt(self):
        self.assertFalse(Failed() > Failed())
        self.assertFalse(NotStarted() > NotStarted())
        self.assertFalse(InProgress() > InProgress())
        self.assertFalse(InProgress(5) > InProgress(5))
        self.assertFalse(Succeeded() > Succeeded())

        self.assertGreater(Succeeded(), Failed())
        self.assertGreater(Succeeded(), NotStarted())
        self.assertGreater(Succeeded(), InProgress(0))
        self.assertGreater(Succeeded(), InProgress(100))
        self.assertGreater(InProgress(100), NotStarted())
        self.assertGreater(InProgress(0), Failed())
        self.assertGreater(InProgress(6), InProgress(5))
        self.assertGreater(NotStarted(), Failed())

    def test_gte(self):
        self.assertGreaterEqual(Failed(), Failed())
        self.assertGreaterEqual(NotStarted(), NotStarted())
        self.assertGreaterEqual(InProgress(), InProgress())
        self.assertGreaterEqual(InProgress(5), InProgress(5))
        self.assertGreaterEqual(Succeeded(), Succeeded())
        self.assertGreaterEqual(Succeeded(), Failed())
        self.assertGreaterEqual(Succeeded(), NotStarted())
        self.assertGreaterEqual(Succeeded(), InProgress(0))
        self.assertGreaterEqual(Succeeded(), InProgress(100))
        self.assertGreaterEqual(InProgress(100), NotStarted())
        self.assertGreaterEqual(InProgress(0), Failed())
        self.assertGreaterEqual(InProgress(6), InProgress(5))
        self.assertGreaterEqual(NotStarted(), Failed())

    def test_in_progress(self):
        self.assertFalse(Failed().in_progress)
        self.assertFalse(NotStarted().in_progress)
        self.assertFalse(Succeeded().in_progress)

        self.assertTrue(InProgress(-234 / 27).in_progress)
        self.assertTrue(InProgress(0).in_progress)
        self.assertTrue(InProgress(55).in_progress)
        self.assertTrue(InProgress(44 / 55).in_progress)
        self.assertTrue(InProgress(100).in_progress)
        self.assertTrue(InProgress(1222 / 287.23).in_progress)
