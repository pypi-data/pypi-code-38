import os
import sys
# to pick up dummy_src (ensure in path):
sys.path.append(os.path.basename(__file__))

import pytest
from dummy_src.something import to_be_run_under_test


class TestSomething:

    @pytest.mark.parametrize('data', ['a%s' % i for i in range(1000)])
    def test_some_alg2(self, data):
        to_be_run_under_test()

    def test_some_alg1(self):
        assert True

    def test_some_alg3(self):
        to_be_run_under_test()
        assert False
