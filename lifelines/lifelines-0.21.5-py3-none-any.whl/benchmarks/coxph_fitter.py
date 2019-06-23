from lifelines import CoxPHFitter
from lifelines.datasets import load_rossi
import pandas as pd

class CoxPHSuite:

    def setup(self):
        self.cph = CoxPHFitter()
        self.data = load_rossi()
        self.data20 = pd.concat([load_rossi()] * 20)

    def time_cph_on_rossi(self):
        self.cph.fit(self.data, 'week', 'arrest')


    def time_cph_on_20_rossi(self):
        self.cph.fit(self.data20, 'week', 'arrest')

