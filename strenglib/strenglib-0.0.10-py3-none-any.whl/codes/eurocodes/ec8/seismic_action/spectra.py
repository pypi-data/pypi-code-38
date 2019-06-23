from ..raw.ch3.seismic_action import spectra as spec_raw
# import streng.codes.eurocodes.ec8.raw.ch3.seismic_action.spectra as spec_raw

from dataclasses import dataclass

@dataclass
class SpectraEc8:
    αgR: float
    γI: float
    ground_type: str
    spectrum_type: int
    η: float = 1.0
    q: float = 1.0
    β: float = 0.2

    def __post_init__(self):
        self.αg = self.γI * self.αgR
        self.S = spec_raw.S(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TB = spec_raw.TB(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TC = spec_raw.TC(ground_type=self.ground_type, spectrum_type=self.spectrum_type)
        self.TD = spec_raw.TD(ground_type=self.ground_type, spectrum_type=self.spectrum_type)


    def Se(self, T)-> float:
        return spec_raw.Se(T, self.αg, self.S, self.TB, self.TC, self.TD, self.η)

    def SDe(self, T)-> float:
        return spec_raw.SDe(T, self.Se(T))

    def dg(self)-> float:
        return spec_raw.dg(self.αg, self.S, self.TC, self.TD)

    def Sd(self, T)-> float:
        return spec_raw.Sd(T, self.αg, self.S, self.TB, self.TC, self.TD, self.q, self.β)

    @staticmethod
    def calc_η(ξ):
        return max(0.55, (10. / (5. + ξ)) ** 0.5)