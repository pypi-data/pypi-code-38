import numpy as np

import Orange
from Orange.widgets.tests.base import WidgetTest
from orangecontrib.spectroscopy.widgets.owfft import OWFFT


class TestOWFFT(WidgetTest):

    def setUp(self):
        self.widget = self.create_widget(OWFFT)
        self.ifg_single = Orange.data.Table("IFG_single.dpt")
        self.ifg_seq = Orange.data.Table("agilent/4_noimage_agg256.seq")

    def test_load_unload(self):
        self.send_signal("Interferogram", self.ifg_single)
        self.send_signal("Interferogram", None)

    def test_laser_metadata(self):
        """ Test dx in presence/absence of laser metadata """
        self.send_signal("Interferogram", self.ifg_seq)
        self.assertEqual(self.widget.dx, (1 / 1.57980039e+04 / 2) * 4)
        self.send_signal("Interferogram", self.ifg_single)
        self.assertEqual(self.widget.dx, (1 / self.widget.laser_wavenumber / 2))

    def test_respect_custom_dx(self):
        """ Setting new data should not overwrite custom dx value """
        self.send_signal("Interferogram", self.ifg_single)
        self.widget.dx_HeNe = False
        self.widget.dx = 5
        self.widget.dx_changed()
        self.send_signal("Interferogram", self.ifg_single)
        self.assertEqual(self.widget.dx, 5)

    def test_keep_metas(self):
        self.widget.autocommit = True
        input = self.ifg_seq
        self.send_signal(OWFFT.Inputs.data, input)
        spectra = self.get_output(OWFFT.Outputs.spectra)
        phases = self.get_output(OWFFT.Outputs.phases)
        np.testing.assert_equal(input.metas, spectra.metas)
        np.testing.assert_equal(input.metas, phases.metas[:, :input.metas.shape[1]])
