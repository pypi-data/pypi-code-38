import numpy as np
import math
from ..common.io.output import OutputTable, OutputString, OutputExtended
from dataclasses import dataclass


@dataclass
class BilinearCurve:
    ay: float
    au: float
    dy: float
    du: float
    a0: float = 0.
    d0: float = 0.

    @property
    def μ(self):
        return (self.du-self.d0) / (self.dy-self.d0)

    @property
    def kel(self):
        return (self.ay - self.a0) / (self.dy - self.d0)

    @property
    def kinel(self):
        return (self.au - self.ay) / (self.du - self.dy)

    @property
    def α(self):
        ### hardening
        return self.kinel / self.kel

    @property
    def β0(self):
        ### ewaution 3-6 in Fema440
        μ = self.μ
        α = self.α
        return (2 / math.pi) * ((μ - 1) * (1 - α)) / (μ * (1 + α * μ - α))

    @property
    def d_array(self):
        return np.array([self.d0, self.dy, self.du])

    @property
    def a_array(self):
        return np.array([self.a0, self.ay, self.au])

    @property
    def T0(self):
        return 2*math.pi*((self.dy-self.d0)/(self.ay - self.a0))**0.5

    # def Teq(self, T0):
    #     ### eqaution 3-5 in Fema440
    #     μ = self.μ
    #     α = self.α
    #     T0 = self.T0
    #     if μ <= 1.0:
    #         return T0
    #     else:
    #         return T0 * (μ / (1 + α * μ - α)) ** 0.5

    @property
    def all_quantities(self):
        out = OutputTable()
        out.data.append({'quantity': 'x_0', 'value': self.d0})
        out.data.append({'quantity': 'x_y', 'value': self.dy})
        out.data.append({'quantity': 'x_u', 'value': self.du})
        out.data.append({'quantity': 'y_0', 'value': self.a0})
        out.data.append({'quantity': 'y_y', 'value': self.ay})
        out.data.append({'quantity': 'y_u', 'value': self.au})
        out.data.append({'quantity': 'kel', 'value': self.kel})
        out.data.append({'quantity': 'kinel', 'value': self.kinel})
        out.data.append({'quantity': 'μ', 'value': self.μ})
        out.data.append({'quantity': 'α', 'value': self.α})
        return out

@dataclass
class Bilin:
    xtarget: float = 0.0
    dropstrength: float = 0.75
    elastoplastic: bool = False
    allowa010: bool = True
    x_ini: np.array = np.array([])
    y_ini: np.array = np.array([])
    EPSILON: float = 0.000001

    def __post_init__(self):
        self.bilinear_curve = BilinearCurve(0., 0., 0., 0.)
        self.output = OutputExtended()
        self.output.OutputStrings['main'] = OutputString(data=['Bilin main output'])
        self.output.OutputTables['InitialCurve'] = OutputTable()
        self.output.OutputTables['Iterations'] = OutputTable()
        self.output.OutputTables['BilinearCurve'] = OutputTable()

    def load_space_delimited(self, fname, delimiter=' '):
        self.x_ini, self.y_ini = np.loadtxt(fname, delimiter=delimiter, usecols=(0, 1), unpack=True)

    def load_space_delimited_string(self, text, delimiter=' '):
        self.x_ini = np.array([], dtype=np.float)
        self.y_ini = np.array([], dtype=np.float)
        spl = text.splitlines()
        for ln in spl:
            xy = ln.split(delimiter)
            self.x_ini = np.append(self.x_ini, xy[0])
            self.y_ini = np.append(self.y_ini, xy[1])
        self.x_ini = self.x_ini.astype(float)
        self.y_ini = self.y_ini.astype(float)

    @staticmethod
    def __curve_to_xcheck(x, y, xtarget):
        if xtarget == 0.0:
            return x, y

        if xtarget > max(x):
            xtarget = max(x)
        _ytarget = float(np.interp(xtarget, x, y))

        # Κρατώ μόνο τις τιμές μέχρι μία πρίν από το xtarget
        _x = x[(x < xtarget)]
        _y = y[0:len(_x)]

        # Προσθέτω τα x, y της παρεμβολής
        _x = np.append(_x, xtarget)
        _y = np.append(_y, _ytarget)

        return _x, _y

    @staticmethod
    def __get_area(x, y):
        return np.trapz(y, x)

    def calc(self):

        for i in range(len(self.x_ini)):
            self.output.OutputTables['InitialCurve'].data.append({'x': self.x_ini[i],
                                                                  'y': self.y_ini[i]})

        # Βρίσκω την αρχική μετατόπιση σε περίπτωση που δεν είναι 0
        x_ini0 = self.x_ini[0]

        self.output.OutputStrings['main'].data.append('')
        self.output.OutputStrings['main'].data.append(f'Αρχική μετατόπιση: {x_ini0}')

        ymax = max(self.y_ini)
        i_ymax = np.argmax(self.y_ini)

        y_max_to_end = self.y_ini[i_ymax:]
        x_max_to_end = self.x_ini[i_ymax:]

        i = 0
        while y_max_to_end[i] > self.dropstrength * ymax and i < len(y_max_to_end) - 1:
            i += 1
        x_for_dropstrength = x_max_to_end[i]

        x_target = min(x_for_dropstrength, self.xtarget)

        # Κρατώ την καμπύλη μέχρι το xtarget, αν υπάρχει
        x_xcheck, y_xcheck = self.__curve_to_xcheck(self.x_ini, self.y_ini, x_target)

        # Αφαιρώ την αρχική μετατόπιση ώστε η καμπύλη να ξεκινά από το (0, 0)
        x_xcheck = x_xcheck - x_ini0

        # self.output.log_text.append('')
        # self.output.log_text.append('X values μέχρι το xtarget, αφαιρώντας (αν υπάρχει) την αρχική μετατόπιση')
        # self.output.log_text.append(str(x_xcheck))
        # self.output.log_text.append('')
        # self.output.log_text.append('Y values μέχρι το xtarget')
        # self.output.log_text.append(str(y_xcheck))

        # Βρίσκω τις δυσκαμψίες σε κάθε βήμα
        # Αλλάχω προσωρινά το x(0) για να μη διαιρεί με 0
        x_xcheck[0] = self.EPSILON
        k = np.divide(y_xcheck, x_xcheck)
        x_xcheck[0] = 0.0

        # self.output.log_text.append('')
        # self.output.log_text.append('Δυσκαμψίες (y(i)/x(i)')
        # self.output.log_text.append(str(k))

        y02 = 0.2 * max(y_xcheck)
        x02 = float(np.interp(y02, y_xcheck, x_xcheck))

        k02 = y02 / x02

        self.output.OutputStrings['main'].data.append('')
        self.output.OutputStrings['main'].data.append('Έλεγχος στο 20% του ymax')
        self.output.OutputStrings['main'].data.append(f'x(02)={x02}, y(02)={y02}. Οπότε k(02)={k02}')

        # Βρίσκω το εμβαρό
        area = self.__get_area(x_xcheck, y_xcheck)
        self.output.OutputStrings['main'].data.append('')
        self.output.OutputStrings['main'].data.append(f'Εμβαδό καμπύλης: {area}')

        # _iterations_dict = NamedLogTable('Iterations')
        iteration_number = 0
        kel = k02
        error = 100.
        while error > self.EPSILON:
            iteration_number += 1  # This is the same as count = count + 1

            x_y, y_y, x_u, y_u, kinel, k_06 = self.iteration(x_xcheck, y_xcheck, kel, area)
            error = np.abs((kel - k_06) / k_06)

            self.output.OutputTables['Iterations'].data.append({'iteration': iteration_number,
                                                                'x_y': x_y,
                                                                'y_y': y_y,
                                                                'x_u': x_u,
                                                                'y_u': y_u,
                                                                'kinel': kinel,
                                                                'kel': kel,
                                                                'k_06': k_06,
                                                                'error': error})


            self.bilinear_curve = BilinearCurve(ay=y_y,
                                                au=y_u,
                                                dy=x_y+x_ini0,
                                                du=x_u+x_ini0,
                                                a0=0.,
                                                d0=+x_ini0)
            kel = k_06

            if iteration_number > 1000:
                break

        for i in range(len(self.bilinear_curve.d_array)):
            self.output.OutputTables['BilinearCurve'].data.append({'x': self.bilinear_curve.d_array[i],
                                                                   'y': self.bilinear_curve.a_array[i]})

    def iteration(self, x, y, kel, area):
        rcount = len(x) - 1
        ymax = max(y)

        # ********** Αρχικός υπολογισμός *****************
        # if y[rcount - 1] >= (2 * ymax + y[rcount]) / 3.0 and y[rcount] <= (2 * ymax + y[rcount]) / 3.0:
        #     y_u = y[rcount - 1]
        # else:
        #     y_u = (2 * ymax + y[rcount]) / 3.0
        y_u = (2 * ymax + y[rcount]) / 3.0

        x_u = x[rcount]

        x_y = (2 * area - x[rcount] * y_u) / (kel * x[rcount] - y_u)
        y_y = kel * x_y

        kinel = (y_u - y_y) / (x_u - x_y)

        # ********** 2η περίπτωση kinel/kel>0.1 *****************
        if self.allowa010 == False and kinel / kel > 0.1:
            alpha = 1.
            beta = -2. * x_u * kel
            gamma = 1.8 * area * kel + 0.1 * (kel * x_u) ** 2
            y_u = (-beta - (beta * beta - 4 * alpha * gamma) ** 0.5) / (2. * alpha)
            x_y = (y_u - 0.1 * kel * x_u) / (0.9 * kel)
            y_y = kel * x_y

            # ********** 3η περίπτωση Ελαστοπλαστικό ή kinel<0 *****************
        if self.elastoplastic == True or kinel < 0.0:
            alpha = 1.
            beta = -2. * x_u
            gamma = 2. * area / kel
            x_y = (-beta - (beta * beta - 4 * alpha * gamma) ** 0.5) / (2. * alpha)
            y_y = x_y * kel
            y_u = y_y

        y_06 = 0.6 * y_y
        x_06 = float(np.interp(y_06, y, x))
        k_06 = y_06 / x_06

        return x_y, y_y, x_u, y_u, kinel, k_06


    # def results_kel(self):
    #     return self.y_results[1] / self.x_results[1]
    #
    # def results_kinel(self):
    #     return (self.y_results[2] - self.y_results[1]) / (self.x_results[2] - self.x_results[1])
    #
    # def results_ductility(self):
    #     return self.x_results[2] / self.x_results[1]
    #
    # def results_hardening(self):
    #     return self.results_kinel()/self.results_kel()


    def __str__(self):
        # return ('\n').join((self.output.log_text.text_list))
        return self.output.OutputStrings['main'].__str__()
