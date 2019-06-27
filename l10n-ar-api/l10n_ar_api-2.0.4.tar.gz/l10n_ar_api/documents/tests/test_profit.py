# -*- coding: utf-8 -*-

from l10n_ar_api.documents import tribute
import pytest


class TestProfit:

    @pytest.fixture(scope="module")
    def profit(self):
        return tribute.Tribute.get_tribute('profit')

    @pytest.fixture(scope="module")
    def goods(self):
        return tribute.Activity(100000, 90, 2.0)

    def test_calculate_retention_without_activity(self, profit):
        with pytest.raises(AttributeError):
            profit.calculate_value(0, 0)

    """ Tests sin acumulados """
    def test_calculate_retention_without_accumulated_less_than_minimum(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(0, 50000)[1] == 0

    def test_calculate_retention_without_accumulated_less_than_minimum_tax(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(0, 102000)[1] == 0

    def test_calculate_retention_without_accumulated(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(0, 200000)[1] == 2000

    """ Tests con acumulados """
    def test_calculate_retention_with_accumulated_less_than_minimum(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(40000, 50000)[1] == 0

    def test_calculate_retention_with_accumulated_less_than_minimum_tax(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(50000, 70000)[1] == 400

    def test_calculate_retention_with_accumulated_less_than_minimum_tax_no_val(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(50000, 52000)[1] == 0

    def test_calculate_retention_with_accumulated_equal_than_minimum(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(100000, 5000)[1] == 100

    def test_calculate_retention_with_accumulated_higher_than_minimum(self, profit, goods):
        profit.activity = goods
        assert profit.calculate_value(150000, 5000)[1] == 100

    def test_calculate_retention_with_accumulated_higher_than_minimum_without_retention_before(
            self, profit, goods):
        """
        En el caso que sea la primer retencion del mes, si ya sobrepaso el acumulado, se debe sumar lo no retenido
        """
        profit.activity = goods
        assert profit.calculate_value(102000, 5000)[1] == 140
