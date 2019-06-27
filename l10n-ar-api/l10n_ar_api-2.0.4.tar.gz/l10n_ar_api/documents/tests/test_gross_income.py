# -*- coding: utf-8 -*-

from l10n_ar_api.documents import tribute
import pytest


class TestGrossIncome:

    @pytest.fixture(scope="module")
    def gross_income_tribute(self):
        return tribute.Tribute.get_tribute('gross_income')

    def test_calculate_retention_without_amount_to_pay(self, gross_income_tribute):
        values = gross_income_tribute.calculate_value(0)
        assert not values[0]
        assert not values[1]

    def test_calculate_retention_without_percentage_and_amount_to_pay(self, gross_income_tribute):
        values = gross_income_tribute.calculate_value(500.0)
        assert values[0] == 500.0
        assert not values[1]

    def test_calculate_retention_with_percentage_and_amount_to_pay(self, gross_income_tribute):
        gross_income_tribute.percentage = 2.0
        values = gross_income_tribute.calculate_value(500.0)
        assert values[0] == 500.0
        assert values[1] == 10.0

    def test_calculate_retention_with_higher_than_minimum(self, gross_income_tribute):
        gross_income_tribute.percentage = 2.0
        gross_income_tribute.minimum_no_aplicable = 400.0
        values = gross_income_tribute.calculate_value(500.0)
        assert values[0] == 500.0
        assert values[1] == 10.0

    def test_calculate_retention_with_less_than_minimum(self, gross_income_tribute):
        gross_income_tribute.percentage = 2.0
        gross_income_tribute.minimum_no_aplicable = 400
        values = gross_income_tribute.calculate_value(300.0)
        assert values[0] == 300.0
        assert values[1] == 0.0
