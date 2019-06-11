from toon.input.clock import MonoClock
from timeit import default_timer


def test_clock():
    clk = MonoClock()
    assert(clk.get_time() > 0)
    assert(clk.getTime() > 0)
    clk = MonoClock()
