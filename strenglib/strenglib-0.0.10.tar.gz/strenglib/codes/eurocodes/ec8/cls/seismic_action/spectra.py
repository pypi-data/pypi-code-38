from dataclasses import dataclass

from ...raw.ch3.seismic_action import spectra as spec_raw


@dataclass
class SpectraEc8:
    """Eurocode 8 response spectra

    If αgR values are given in g, displacements should be multiplied with 9.81

    Attributes:
        αgR (float): reference peak ground acceleration on type A ground
        γI (float): importance factor
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2
        η (float): value of the damping correction factor
        q (float): behaviour factor
        β (float): lower bound factor for the horizontal design spectrum. Recommended value for β is 0.2

    """
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
        """float: The elastic acceleration response spectrum"""
        return spec_raw.Se(T, self.αg, self.S, self.TB, self.TC, self.TD, self.η)

    def SDe(self, T)-> float:
        """float: The elastic displacement response spectrum"""
        return spec_raw.SDe(T, self.Se(T))

    def dg(self)-> float:
        """float: Design ground displacement"""
        return spec_raw.dg(self.αg, self.S, self.TC, self.TD)

    def Sd(self, T)-> float:
        """float: Design spectrum for elastic analysis"""
        return spec_raw.Sd(T, self.αg, self.S, self.TB, self.TC, self.TD, self.q, self.β)

