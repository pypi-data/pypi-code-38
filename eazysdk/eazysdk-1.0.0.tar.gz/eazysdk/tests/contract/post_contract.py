from ... import main
from ...exceptions import ParameterNotAllowedError
from ...exceptions import InvalidParameterError
from ...exceptions import InvalidStartDateError
from ...exceptions import ResourceNotFoundError
from ...settings import Settings as s
import unittest


class Test(unittest.TestCase):
    def setUp(self):
        self.eazy = main.EazySDK().post

    def test_ad_hoc_post_contract(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice'
            )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_post_contract_auto_fix_start_date(self):
        s.contracts['auto_start_date'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
            '2018-06-15', False, 'Until Further Notice',
            'Switch to further notice'
        )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_post_contract_auto_fix_termination_type(self):
        s.contracts['auto_fix_ad_hoc_termination_type'] = True
        req = self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice',
            )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_auto_fix_at_the_end(self):
        s.contracts['auto_fix_ad_hoc_at_the_end'] = True
        req = self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until further notice',
                'expire',
            )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_post_contract_gift_aid_true(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
            '2019-08-15', True, 'Until Further Notice',
            'Switch to further notice'
            )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_post_contract_allow_additional_ref(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', additional_reference='test-0001'
            )
        self.assertIn('SDKTST-', req)

    def test_ad_hoc_invalid_customer_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract(
                '10a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until Further Notice',
                'Switch to further notice',
                )
        self.assertIn('The requested resource could not', str(e.exception))

    def test_ad_hoc_invalid_start_date_throws_error(self):
        s.contracts['auto_start_date'] = False
        with self.assertRaises(InvalidStartDateError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2018-06-15', False, 'Until Further Notice',
                'Switch to further notice',
            )
        self.assertIn('is not a valid start date', str(e.exception))

    def test_ad_hoc_invalid_termination_type_throws_error(self):
        s.contracts['auto_start_date'] = False
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Take certain number of debits',
                'Switch to further notice',
            )
        self.assertIn('termination_type must be set to', str(e.exception))

    def test_ad_hoc_invalid_at_the_end_throws_error(self):
        s.contracts['auto_fix_ad_hoc_at_the_end'] = False
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until further notice',
                'Expire',
            )
        self.assertIn('must be set to Switch to further', str(e.exception))

    def test_ad_hoc_passing_initial_amount_throws_error(self):
        with self.assertRaises(ParameterNotAllowedError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until Further Notice',
                'Switch to further notice', initial_amount='1.00'
            )
        self.assertIn('cannot be passed on ad_hoc contracts', str(e.exception))

    def test_ad_hoc_passing_extra_initial_amount_throws_error(self):
        with self.assertRaises(ParameterNotAllowedError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until Further Notice',
                'Switch to further notice', extra_initial_amount='1.00'
            )
        self.assertIn('cannot be passed on ad_hoc contracts', str(e.exception))

    def test_ad_hoc_passing_final_amount_throws_error(self):
        with self.assertRaises(ParameterNotAllowedError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'adhoc_monthly_free',
                '2019-08-15', False, 'Until Further Notice',
                'Switch to further notice', final_amount='1.00'
            )
        self.assertIn('cannot be passed on ad_hoc contracts', str(e.exception))

    def test_invalid_schedule_name_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'not_a_schedule',
                '2019-08-15', False, 'Until Further Notice',
                'Switch to further notice',
            )
        self.assertIn('is not a valid schedule', str(e.exception))

    # All non-adhoc weekly schedules will fail.
    def test_weekly_post_contract_until_further_notice(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday'
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_post_contract_take_certain_number_of_debits(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Take certain number of debits',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            number_of_debits=10
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_post_contract_end_on_exact_date(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'End on exact date',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            termination_date='2020-01-15'
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_auto_fix_start_date(self):
        s.contracts['auto_start_date'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-06-01', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_Week='Monday'
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            initial_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_extra_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            extra_initial_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_final_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            final_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_additional_reference(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
            '2019-07-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_week='Monday',
            additional_reference='test-0001'
            )
        self.assertIn('SDKTST-', req)

    def test_weekly_invalid_customer_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract(
                '0a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_week=1, termination_date='2019-10-15'
            )
        self.assertIn('The requested resource could not', str(e.exception))

    def test_weekly_invalid_start_date_throws_error(self):
        s.contracts['auto_start_date'] = False
        with self.assertRaises(InvalidStartDateError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-05-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_week=1, termination_date='2019-10-15'
            )
        self.assertIn('is not a valid start date', str(e.exception))

    def test_weekly_invalid_payment_date_in_week_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_week=6, termination_date='2019-10-15'
            )
        self.assertIn('must be set to 15', str(e.exception))

    def test_weekly_frequency_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', payment_amount=10.00,
                payment_day_in_week=1, termination_date='2019-10-15'
            )
        self.assertIn('frequency must be passed', str(e.exception))

    def test_weekly_payment_amount_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_day_in_week=1, termination_date='2019-10-15'
            )
        self.assertIn('payment amount must be passed', str(e.exception))

    def test_weekly_certain_debits_number_of_debits_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'Take certain number of debits',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_week=1
            )
        self.assertIn('number_of_debits must be passed', str(e.exception))

    def test_weekly_end_on_date_termination_date_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_week=1
            )
        self.assertIn('termination_date must be passed', str(e.exception))

    def test_weekly_end_on_exact_date_termination_date_cannot_be_less(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'weekly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_week=1,
                termination_date='2019-06-14'
            )
        self.assertIn('is not a valid termination date', str(e.exception))

    def test_monthly_post_contract_until_further_notice(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_post_contract_take_certain_number_of_debits(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Take certain number of debits',
            'Switch to further notice', frequency=1, payment_amount=10.00,
            payment_day_in_month=15, number_of_debits=10
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_post_contract_end_on_exact_date(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'End on exact date',
            'Switch to further notice', frequency=1, payment_amount=10.00,
            payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_auto_fix_start_date(self):
        s.contracts['auto_start_date'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-06-01', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=13
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_auto_fix_payment_day_in_month(self):
        s.contracts['auto_fix_payment_day_in_month'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-06-22', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=1
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15, initial_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_extra_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            extra_initial_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_final_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15, final_amount=10.50
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_additional_reference(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            additional_reference='test-004'
            )
        self.assertIn('SDKTST-', req)

    def test_monthly_invalid_customer_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract(
                '10a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('The requested resource could not', str(e.exception))

    def test_monthly_invalid_schedule_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'not_a_schedule',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('is not a valid schedule', str(e.exception))

    def test_monthly_invalid_start_date_throws_error(self):
        s.contracts['auto_start_date'] = False
        with self.assertRaises(InvalidStartDateError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-05-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('is not a valid start date', str(e.exception))

    def test_monthly_invalid_payment_date_in_month_throws_error(self):
        s.contracts['auto_fix_payment_day_in_month'] = False
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=1, termination_date='2019-10-15'
            )
        self.assertIn('must be set to 15', str(e.exception))

    def test_monthly_frequency_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('frequency must be passed', str(e.exception))

    def test_monthly_payment_amount_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_day_in_month=15, termination_date='2019-10-15'
            )
        self.assertIn('payment amount must be passed', str(e.exception))

    def test_monthly_certain_debits_number_of_debits_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'Take certain number of debits',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15
            )
        self.assertIn('number_of_debits must be passed', str(e.exception))

    def test_monthly_end_on_date_termination_date_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15
            )
        self.assertIn('termination_date must be passed', str(e.exception))

    def test_monthly_end_on_exact_date_termination_date_cannot_be_less(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'monthly_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15,
                termination_date='2019-06-14'
            )
        self.assertIn('is not a valid termination date', str(e.exception))

    def test_annual_post_contract_until_further_notice(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_post_contract_take_certain_number_of_debits(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Take certain number of debits',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            payment_month_in_year=8, number_of_debits=10
            )
        self.assertIn('SDKTST-', req)

    def test_annual_post_contract_end_on_exact_date(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'End on exact date',
            'Switch to further notice', frequency=1, payment_amount=10.00,
            payment_day_in_month=15, payment_month_in_year=8,
            termination_date='2019-10-15'
            )
        self.assertIn('SDKTST-', req)

    def test_annual_auto_fix_start_date(self):
        s.contracts['auto_start_date'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=13,
            payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_auto_fix_payment_day_in_month(self):
        s.contracts['auto_fix_payment_day_in_month'] = True
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=1,
            payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            initial_amount=10.50, payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_extra_initial_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            extra_initial_amount=10.50, payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_final_amount(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15, final_amount=10.50,
            payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_additional_reference(self):
        req = self.eazy.contract(
            '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
            '2019-08-15', False, 'Until Further Notice',
            'Switch to further notice', frequency=1,
            payment_amount=10.00, payment_day_in_month=15,
            additional_reference='test-004', payment_month_in_year=8
            )
        self.assertIn('SDKTST-', req)

    def test_annual_invalid_customer_throws_error(self):
        with self.assertRaises(ResourceNotFoundError) as e:
            self.eazy.contract(
                '10a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15',
                payment_month_in_year=8
            )
        self.assertIn('The requested resource could not', str(e.exception))

    def test_annual_invalid_start_date_throws_error(self):
        s.contracts['auto_start_date'] = False
        with self.assertRaises(InvalidStartDateError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-05-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15',
                payment_month_in_year=5
            )
        self.assertIn('is not a valid start date', str(e.exception))

    def test_annual_invalid_payment_date_in_month_throws_error(self):
        s.contracts['auto_fix_payment_day_in_month'] = False
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=2, termination_date='2019-10-15',
                payment_month_in_year=8
            )
        self.assertIn('must be set to 15', str(e.exception))

    def test_annual_invalid_payment_month_in_year_throws_error(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1, payment_amount=10.00,
                payment_day_in_month=15, termination_date='2019-10-15',
                payment_month_in_year=6
            )
        self.assertIn('must be set to 08', str(e.exception))

    def test_annual_payment_amount_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_day_in_month=15, termination_date='2019-10-15',
                payment_month_in_year=8
            )
        self.assertIn('payment amount must be passed', str(e.exception))

    def test_annual_certain_debits_number_of_debits_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'Take certain number of debits',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15,
                payment_month_in_year=8
            )
        self.assertIn('number_of_debits must be passed', str(e.exception))

    def test_annual_end_on_date_termination_date_must_be_passed(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15,
                payment_month_in_year=8
            )
        self.assertIn('termination_date must be passed', str(e.exception))

    def test_annual_end_on_exact_date_termination_date_cannot_be_less(self):
        with self.assertRaises(InvalidParameterError) as e:
            self.eazy.contract(
                '310a826b-d095-48e7-a55a-19dba82c566f', 'annual_free',
                '2019-08-15', False, 'End on exact date',
                'Switch to further notice', frequency=1,
                payment_amount=10.00, payment_day_in_month=15,
                termination_date='2019-06-14', payment_month_in_year=8
            )
        self.assertIn('is not a valid termination date', str(e.exception))
