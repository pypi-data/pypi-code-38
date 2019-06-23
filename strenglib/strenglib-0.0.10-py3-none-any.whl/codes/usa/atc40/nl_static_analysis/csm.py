from dataclasses import dataclass
import numpy as np
from ..raw.ch8 import csm as csm_atc40
from .....common.math.numerical import intersection
from .....tools.bilin import Bilin
from .....codes.eurocodes.ec8.seismic_action import spectra as spec_ec8

@dataclass
class StructureProperties:
    φ: np.ndarray
    m: np.ndarray
    pushover_curve_F: np.ndarray
    pushover_curve_δ: np.ndarray
    behavior: str


    def __post_init__(self):
        self.PF1 = csm_atc40.PF1(self.m, self.φ)
        self.α1 = csm_atc40.α1(self.m, self.φ)
        self.φroof1 = self.φ[-1]
        self.Sa = csm_atc40.Sa(V=self.pushover_curve_F,
                                        W=sum(self.m),
                                        α1=self.α1)
        self.Sd = csm_atc40.Sd(Δroof=self.pushover_curve_δ,
                                        PF1=self.PF1,
                                        φroof1=self.φroof1)


@dataclass
class Demand:
    T_range: np.ndarray
    Sa: np.ndarray
    Sd: np.ndarray
    TC: float

    def ec8_elastic(self, αgR: float, γI: float, ground_type: str, spectrum_type: int, η = 1.0, q = 1.0, β = 0.2):
        _spec_ec8 = spec_ec8.SpectraEc8(αgR, γI, ground_type, spectrum_type, η, q, β)
        self.Sa = _spec_ec8.Se(self.T_range)
        self.Sd = _spec_ec8.SDe(self.T_range)
        self.TC = _spec_ec8.TC

@dataclass
class CapacitySpectrumMethod:
    structure: StructureProperties
    demand: Demand

    first_try_case = 'intersection'


    @property
    def Sd_first_try(self):
        if self.first_try_case == 'intersection':
            x_solve, y_solve = intersection(self.demand.Sd, self.demand.Sa, self.structure.Sd, self.structure.Sa)
            return x_solve[-1]
        else:
            return 0.


    def __iterate_SR(self, x0):
        bl =Bilin(xtarget=x0)
        bl.x_ini, bl.y_ini = self.structure.Sd, self.structure.Sa
        bl.calc()

        β0 = bl.bilinear_curve.β0
        βeff = csm_atc40.βeff(0.05, β0, self.structure.behavior)

        Teff = bl.bilinear_curve.Teq

        SRA = csm_atc40.SRA(βeff, self.structure.behavior)
        SRV = csm_atc40.SRV(βeff, self.structure.behavior)

        if Teff > self.demand.TC:
            SR = SRV
        else:
            SR = SRA

        _Sa = SR*self.demand.Sa
        _Sd = SR*self.demand.Sd

        x_solve, y_solve = intersection(_Sd, _Sa, self.structure.Sd, self.structure.Sa)
        return x_solve[-1]

    def calc_performance_point(self):
        x_i = self.Sd_first_try
        iter_num = 0
        error = 100.
        while error > 0.001:
            x_new = self.__iterate_SR(x_i)
            error = abs((x_new - x_i) / x_i)
            x_i = x_new
            iter_num = iter_num + 1
            print(f'iteration: {iter_num} x={x_i:.4f} error={error:.2%}')

        print()
        print(f'sulution: Sd = {x_i:.4f}m')