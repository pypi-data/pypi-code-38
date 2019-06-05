import unittest
import fclib.compound


class TestCompound(unittest.TestCase):
    def setUp(self):
        self.principal_amount = 500000
        self.contribution_amount = 40000
        self.rate = 0.055860255
        self.periods = 1
        self.years = 23
        self.valorization = 3529220.56

    def test_rate(self):
        rate_value = fclib.compound.rate(0.5,
                                         self.valorization,
                                         self.principal_amount,
                                         self.contribution_amount,
                                         self.years,
                                         self.periods)
        self.assertEqual(rate_value, 0.055860254959179775)

    def test_rate_failure_to_converge(self):
        rate_value = fclib.compound.rate(50,
                                         self.valorization,
                                         self.principal_amount,
                                         self.contribution_amount,
                                         self.years,
                                         self.periods)
        self.assertIsNone(rate_value)
