from unittest import TestCase
from pandas import Series
from sedatatools.helpers.bracket_calculations import median_calculation


class TestCalc_median_from_brackets(TestCase):
    def test_calc_median_from_brackets(self):
        """
            # first option
            # original value:    $47,652
            # this function :    $47694
            # error    -0.09 %
            # C# function   :    $47, 569
            # error    -0.17
            # second option doesnt work without distribution
            """
        bracket_v = [196,
                     233,
                     205,
                     200,
                     319,
                     213,
                     170,
                     130,
                     167,
                     251,
                     448,
                     480,
                     165,
                     88,
                     161,
                     86]
        bracket_c = [
            'Less than $10,000',
            '$10,000 to $14,999',
            '$15,000 to $19,999',
            '$20,000 to $24,999',
            '$25,000 to $29,999',
            '$30,000 to $34,999',
            '$35,000 to $39,999',
            '$40,000 to $44,999',
            '$45,000 to $49,999',
            '$50,000 to $59,999',
            '$60,000 to $74,999',
            '$75,000 to $99,999',
            '$100,000 to $124,999',
            '$125,000 to $149,999',
            '$150,000 to $199,999',
            '$200,000 or More',
        ]
        test_ser = Series(data=bracket_v, index=bracket_c)
        self.assertEqual(median_calculation.calculate_median_from_brackets(test_ser), 47694)

    def test_calc_median_from_brackets_2(self):
        """
            # first option
            # original value:    $47,652
            # this function :    $47694
            # error    -0.09 %
            # C# function   :    $47, 569
            # error    -0.17
            # second option doesnt work without distribution
            """
        bracket_v = [6,
                     18,
                     9,
                     10,
                     4,
                     3,
                     ]
        bracket_c = [
            '$10 to $15',
            '$15 to $20',
            '$20 to $25',
            '$25 to $30',
            '$30 to $35',
            '$35 to $40',
        ]
        test_ser = Series(data=bracket_v, index=bracket_c)
        self.assertEqual(median_calculation.calculate_median_from_brackets(test_ser), 20)

    def test_calc_mean_from_brackets(self):
        bracket_v = [196,
                     233,
                     205,
                     200,
                     319,
                     213,
                     170,
                     130,
                     167,
                     251,
                     448,
                     480,
                     165,
                     88,
                     161,
                     86]
        bracket_c = [
            'Less than $10,000',
            '$10,000 to $14,999',
            '$15,000 to $19,999',
            '$20,000 to $24,999',
            '$25,000 to $29,999',
            '$30,000 to $34,999',
            '$35,000 to $39,999',
            '$40,000 to $44,999',
            '$45,000 to $49,999',
            '$50,000 to $59,999',
            '$60,000 to $74,999',
            '$75,000 to $99,999',
            '$100,000 to $124,999',
            '$125,000 to $149,999',
            '$150,000 to $199,999',
            '$200,000 or More',
        ]
        test_ser = Series(data=bracket_v, index=bracket_c)
        self.assertEqual(median_calculation.calculate_mean_from_brackets(test_ser), 60290)
