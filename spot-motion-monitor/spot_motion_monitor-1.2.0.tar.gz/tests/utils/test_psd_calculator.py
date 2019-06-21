#------------------------------------------------------------------------------
# Copyright (c) 2018 LSST Systems Engineering
# Distributed under the MIT License. See LICENSE for more information.
#------------------------------------------------------------------------------
import numpy as np
import pytest

from spot_motion_monitor.utils import psd_calculator

class TestPsdCalculator:

    def test_calculation(self):
        np.random.seed(2000)
        L = 10
        x = np.random.normal(250.0, 1.0, L)
        y = np.random.normal(320.0, 1.0, L)
        fps = 2.0

        xPsd, yPsd, freqs = psd_calculator(x, y, fps)
        assert freqs.tolist() == pytest.approx([0.2, 0.4, 0.6, 0.8])
        assert xPsd.tolist() == pytest.approx([1.3022891, 2.4072877, 2.96332612, 1.13724273])
        assert yPsd.tolist() == pytest.approx([0.41251254, 0.51454309, 0.56978575, 2.22593171])
