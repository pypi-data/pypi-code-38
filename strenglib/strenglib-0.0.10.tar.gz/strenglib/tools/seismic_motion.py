import math
import numpy as np
from scipy import integrate  # optimize, stats
from dataclasses import dataclass

from ..common.math.numerical import xy_with_endpoints
from ..common.io.output import OutputTable, OutputString, OutputExtended


@dataclass
class Record:
    dt: float = None
    accel: np.array = None

    def __post_init__(self):
        self.step: int = None
        self.time_total: float = None
        self.time: np.array = None
        self.velocity: np.array = None
        self.displacement: np.array = None
        self.Husid_norm: np.array = None
        self.Husid: np.array = None
        self.output = OutputExtended()
        self.output.OutputTables['RecordMotionProperties'] = OutputTable()

        self.props = {'PGA': None,
                       'PGV': None,
                       'PGD': None,
                       'timePGA': None,
                       'timePGV': None,
                       'timePGD': None,
                       'PGVdivPGA': None,
                       'aRMS': None,
                       'vRMS': None,
                       'dRMS': None,
                       'Ia': None,
                       'Ic': None,
                       'SED': None,
                       'CAV': None,
                       'T_Arias5_95': None}

    def load_single_line_textfile(self, filename):
        self.accel = np.loadtxt(filename)


    def calc(self):
        self.steps = len(self.accel)
        self.time_total = (self.steps - 1) * self.dt

        self.time = np.arange(0., self.steps * self.dt, self.dt)

        self.calc_vel_disp()

        self.props['PGA'] = max(np.absolute(self.accel))
        self.props['PGV'] = max(np.absolute(self.velocity))
        self.props['PGD'] = max(np.absolute(self.displacement))
        self.props['timePGA'] = float(np.where(np.absolute(self.accel) == self.props['PGA'])[0]) * self.dt
        self.props['timePGV'] = float(np.where(np.absolute(self.velocity) == self.props['PGV'])[0]) * self.dt
        self.props['timePGD'] = float(np.where(np.absolute(self.displacement) == self.props['PGD'])[0]) * self.dt
        self.props['PGVdivPGA'] = self.props['PGV'] / self.props['PGA']
        self.props['aRMS'] = math.sqrt((1./self.time_total)*integrate.trapz(self.accel * self.accel, self.time ))
        self.props['vRMS'] = math.sqrt((1./self.time_total)*integrate.trapz(self.velocity * self.velocity, self.time ))
        self.props['dRMS'] = math.sqrt((1./self.time_total)*integrate.trapz(self.displacement * self.displacement, self.time ))
        self.props['Ia'] = (math.pi/(2*9.81))*integrate.trapz(self.accel * self.accel, self.time )
        self.props['Ic'] = self.props['aRMS']**1.5 * math.sqrt(self.time_total)
        self.props['SED'] = integrate.trapz(self.velocity * self.velocity, self.time)
        self.props['CAV'] = integrate.trapz(np.absolute(self.accel), self.time)

        self.Husid = math.pi / (2*9.81) * integrate.cumtrapz(self.accel * self.accel, self.time, initial=0.)
        self.Husid_norm = self.Husid / self.props['Ia']

        self.props['T_Arias5_95'] = self.get_significant_duration(0.05, 0.95)

        out = OutputTable.change_dict_to_quantity_value_data(self.props)
        self.output.OutputTables['RecordMotionProperties'].data = out


    def get_significant_duration(self, start_percentage, end_percentage):
        t_start = float(np.interp(start_percentage, self.Husid_norm, self.time))
        t_end = float(np.interp(end_percentage, self.Husid_norm, self.time))
        return t_end-t_start


    def get_spectra(self, damping, startT=0., endT=4., noTs=401):
        _spec = Spectra(accel = self.accel,
                        dt=self.dt)
        return _spec.get_spectra(damping, startT, endT, noTs)


    def show_parameters(self):
        paramlog = []
        paramlog.append('PGA = {:.4f}'.format(self.props['PGA']))
        paramlog.append('time for PGA = {:.4f}'.format(self.props['timePGA']))
        paramlog.append('PGV = {:.4f}'.format(self.props['PGV']))
        paramlog.append('time for PGV = {:.4f}'.format(self.props['timePGV']))
        paramlog.append('PGD = {:.4f}'.format(self.props['PGD']))
        paramlog.append('time for PGD = {:.4f}'.format(self.props['timePGD']))
        paramlog.append('PGV/PGA = {:.4f}'.format(self.props['PGVdivPGA']))
        paramlog.append('aRMS = {:.4f}'.format(self.props['aRMS']))
        paramlog.append('vRMS = {:.4f}'.format(self.props['vRMS']))
        paramlog.append('dRMS = {:.4f}'.format(self.props['dRMS']))
        paramlog.append('Arias Intensity Ia = {:.4f}'.format(self.props['Ia']))
        paramlog.append('Characteristic Intensity Ic = {:.4f}'.format(self.props['Ic']))
        paramlog.append('Specific Energy Density SED = {:.4f}'.format(self.props['SED']))
        paramlog.append('Cumulative Absolute Velocity CAV = {:.4f}'.format(self.props['CAV']))
        paramlog.append('Significant duration (5-95% in Husid plot) = {:.4f}'.format(self.props['T_Arias5_95']))

        return '\n'.join(paramlog)

    def calc_vel_disp(self):
        self.velocity = self.dt * integrate.cumtrapz(self.accel, initial=0.)
        self.displacement = self.dt * integrate.cumtrapz(self.velocity, initial=0.)



@dataclass
class Spectra:
    accel: np.array = np.array([])
    dt: float = None


    @classmethod
    def calculate_time_series(cls, num_steps, num_per, acc, const, omega2, dt):
        """
        Calculates the acceleration, velocity and displacement time series for
        the SDOF oscillator
        :param dict const:
            Constants of the algorithm
        :param np.ndarray omega2:
            Square of the oscillator period
        :returns:
            x_a = Acceleration time series
            x_v = Velocity time series
            x_d = Displacement time series
        """
        x_d = np.zeros([num_steps - 1, num_per], dtype=float)
        x_v = np.zeros_like(x_d)
        x_a = np.zeros_like(x_d)

        for k in range(0, num_steps - 1):
            dug = acc[k + 1] - acc[k]
            z_1 = const['f2'] * dug
            z_2 = const['f2'] * acc[k]
            z_3 = const['f1'] * dug
            z_4 = z_1 / dt
            if k == 0:
                b_val = z_2 - z_3
                a_val = (const['f5'] * b_val) + (const['f4'] * z_4)
            else:
                b_val = x_d[k - 1, :] + z_2 - z_3
                a_val = (const['f4'] * x_v[k - 1, :]) + \
                        (const['f5'] * b_val) + (const['f4'] * z_4)

            x_d[k, :] = (a_val * const['g1']) + (b_val * const['g2']) + \
                        z_3 - z_2 - z_1
            x_v[k, :] = (a_val * const['h1']) - (b_val * const['h2']) - z_4
            x_a[k, :] = (-const['f6'] * x_v[k, :]) - (omega2 * x_d[k, :])

        return x_a, x_v, x_d

    @classmethod
    def NigamJennings(cls, acc, periods, damping, dt):
        add_PGA = False
        if periods[0] == 0:
            periods = np.delete(periods, 0)
            add_PGA = True

        num_steps = len(acc)
        num_per = len(periods)
        omega = (2. * np.pi) / np.array(periods)
        omega2 = omega ** 2.
        omega3 = omega ** 3.
        omega_d = omega * math.sqrt(1.0 - (damping ** 2.))
        const = {'f1': (2.0 * damping) / (omega3 * dt),
                 'f2': 1.0 / omega2,
                 'f3': damping * omega,
                 'f4': 1.0 / omega_d}
        const['f5'] = const['f3'] * const['f4']
        const['f6'] = 2.0 * const['f3']
        const['e'] = np.exp(-const['f3'] * dt)
        const['s'] = np.sin(omega_d * dt)
        const['c'] = np.cos(omega_d * dt)
        const['g1'] = const['e'] * const['s']
        const['g2'] = const['e'] * const['c']
        const['h1'] = (omega_d * const['g2']) - (const['f3'] * const['g1'])
        const['h2'] = (omega_d * const['g1']) + (const['f3'] * const['g2'])
        x_a, x_v, x_d = cls.calculate_time_series(num_steps, num_per, acc, const, omega2, dt)

        spectrum = {'Sa': None,
                    'Sv': None,
                    'Sd': None,
                    'T': None,
                    'PSv': None,
                    'PSa': None,
                    'ASI': None,
                    'VSI': None,
                    'HI': None,
                    'Tp': None}
        spectrum['Sa'] = np.max(np.fabs(x_a), axis=0)
        spectrum['Sv'] = np.max(np.fabs(x_v), axis=0)
        spectrum['Sd'] = np.max(np.fabs(x_d), axis=0)
        spectrum['PSv'] = spectrum['Sd'] * omega
        spectrum['PSa'] = spectrum['Sd'] * omega2
        spectrum['T'] = periods

        if add_PGA:
            pga = np.max(np.fabs(acc))
            periods = np.append(0, periods)
            spectrum['Sa'] = np.append(pga, spectrum['Sa'])
            spectrum['Sv'] = np.append(0, spectrum['Sv'])
            spectrum['Sd'] = np.append(0, spectrum['Sd'])
            spectrum['PSv'] = np.append(0, spectrum['PSv'])
            spectrum['PSa'] = np.append(pga, spectrum['PSa'])
            spectrum['T'] = periods

        xy_ASI = xy_with_endpoints(spectrum['T'], spectrum['Sa'], 0.1, 0.5)
        spectrum['ASI'] = integrate.trapz(xy_ASI[1], xy_ASI[0])

        xy_VSI = xy_with_endpoints(spectrum['T'], spectrum['Sv'], 0.1, 2.5)
        spectrum['VSI'] = integrate.trapz(xy_VSI[1], xy_VSI[0])

        xy_HI = xy_with_endpoints(spectrum['T'], spectrum['PSv'], 0.1, 2.5)
        spectrum['HI'] = integrate.trapz(xy_HI[1], xy_HI[0])

        spectrum['Tp'] = (float(np.where(spectrum['Sa'] == max(spectrum['Sa']))[0]) + 1) * (periods[1] - periods[0])

        return spectrum


    @staticmethod
    def show_spectra_parameters(spectrum):
        paramlog = []
        paramlog.append('Acceleration Spectrum Intensity: ASI = {:.4f}'.format(spectrum['ASI']))
        paramlog.append('Velocity Spectrum Intensity: VSI = {:.4f}'.format(spectrum['VSI']))
        paramlog.append('Housner Intensity: HI = {:.4f}'.format(spectrum['HI']))
        paramlog.append('Predominant Period: Tp = {:.4f}'.format(spectrum['Tp']))

        return '\n'.join(paramlog)





    def get_spectra(self, damping, startT=0., endT=4., noTs=401):
        T = np.linspace(startT, endT, noTs)
        # self.spectrum = NigamJennings(self.accel, T, damping, self.dt)
        return self.NigamJennings(self.accel, T, damping, self.dt)