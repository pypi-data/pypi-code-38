from lifelines import KaplanMeierFitter
from lifelines.datasets import load_rossi
import pandas as pd
import numpy as np

class KaplanMeierFitterSuite:

    def setup(self):
        self.kmf = KaplanMeierFitter()
        self.rossi20 = pd.concat([load_rossi()] * 20)

        N = 10_000
        self.random_durations = np.random.exponential(size=N)
        self.random_censoring = np.random.binomial(1, 0.8, size=N)

    def time_kmf_unique_times_with_censorship(self):
        self.kmf.fit(self.random_durations, self.random_censoring)


    def time_kmf_on_20_rossi(self):
        self.kmf.fit(self.rossi20['week'], self.rossi20['arrest'])

