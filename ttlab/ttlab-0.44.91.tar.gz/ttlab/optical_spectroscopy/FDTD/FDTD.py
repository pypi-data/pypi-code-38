from .FDTD_file_reader import FDTDFileReader
from plotly.offline import init_notebook_mode, iplot, plot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy import constants as sc


class FDTD:

    def __init__(self, filename_cross_section, filename_wavelength, simulation_names):
        self.data = FDTDFileReader.read_data(filename_cross_section=filename_cross_section, filename_wavelength=filename_wavelength, simulation_names=simulation_names)

    def get_wavelength(self, sample):
        return self.data[sample].wavelength

    def get_cross_section(self, sample):
        return self.data[sample].cross_section

    def get_energy(self,sample):
        if self.data[sample].energy is None:
            self.data[sample].energy=self._convert_wavelength_to_energy(self.get_wavelength(sample))

        return self.data[sample].energy

    @property
    def samples(self):
        return self.data.keys()

    def plotly_all(self,energy=False, title=''):
        init_notebook_mode(connected=True)
        data = []
        for sample in self.samples:
            if energy:
                x = self.get_energy(sample)
            else:
                x = self.get_wavelength(sample)
            y = self.data[sample].cross_section
            trace = FDTD._create_x_y_trace(x, y, sample)
            data.append(trace)
        layout = FDTD._get_plotly_layout(title)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def get_fwhm_and_max(self,sample,range=50, show_fit=False, energy=True, fit_order=50):
        coordinate_zero = 0

        if energy:
            x_axis = self.get_energy(sample)
        else:
            print('Not yet implemented')
            return

        transmission = self.get_cross_section(sample)

        ## get close area around maxium to fit
        max_rough_idx = np.argmax(transmission)
        transmission_narrow_max = transmission[max_rough_idx - range:max_rough_idx + range]
        x_axis_narrow_max = x_axis[max_rough_idx - range:max_rough_idx + range]

        ## fit around maximum to get a better (closer) value for the maximum/minimum
        polyfit_max = np.polyfit(x_axis_narrow_max, transmission_narrow_max, fit_order)
        poly1d_max = np.poly1d(polyfit_max)
        x_axis_max_evaluation = np.linspace(x_axis_narrow_max[0], x_axis_narrow_max[-1], 10000)
        transmission_max_evaluation = []
        for x in x_axis_max_evaluation:
            transmission_max_evaluation.append(poly1d_max(x))
        transmission_max_evaluation = np.array(transmission_max_evaluation)
        max_evaluation_idx = np.argmax(transmission_max_evaluation)
        max_value = x_axis_max_evaluation[max_evaluation_idx]

        ## determine closest point to the left of fwhm
        fwhm_hline = coordinate_zero - (coordinate_zero - transmission_max_evaluation[max_evaluation_idx]) / 2
        tmp_fwhm, tmp_fwhm_idx = self._find_nearest(transmission[max_rough_idx:], fwhm_hline)

        tmp_fwhm_idx = tmp_fwhm_idx + max_rough_idx  # insert the max_rough offset again
        transmission_narrow_fwhm = transmission[tmp_fwhm_idx - range:tmp_fwhm_idx + range]
        x_axis_narrow_fwhm = x_axis[tmp_fwhm_idx - range:tmp_fwhm_idx + range]

        # ## fit around this fwhm point to get a better (closer) value for it
        polyfit_fwhm = np.polyfit(x_axis_narrow_fwhm, transmission_narrow_fwhm, fit_order)
        poly1d_fwhm = np.poly1d(polyfit_fwhm)

        x_axis_fwhm_evaluation = np.linspace(x_axis_narrow_fwhm[0], x_axis_narrow_fwhm[-1], 10000)
        transmission_fwhm_evaluation = []
        for x in x_axis_fwhm_evaluation:
            transmission_fwhm_evaluation.append(poly1d_fwhm(x))
        transmission_fwhm_evaluation = np.array(transmission_fwhm_evaluation)

        tmp, fwhm_intersection_idx = self._find_nearest(transmission_fwhm_evaluation, fwhm_hline)
        fwhm_intersection = x_axis_fwhm_evaluation[fwhm_intersection_idx]

        fwhm = 2 * abs(fwhm_intersection - max_value)

        if show_fit:
            fig, ax = plt.subplots()
            ax.plot(x_axis, transmission, 'x')
            ax.plot(x_axis_narrow_max, transmission_narrow_max, 'o')
            ax.plot(x_axis_narrow_max, poly1d_max(x_axis_narrow_max))
            ax.axvline(max_value)
            ax.axhline(fwhm_hline)
            ax.plot(x_axis_max_evaluation, transmission_max_evaluation, 'k')
            ax.plot(x_axis_fwhm_evaluation, transmission_fwhm_evaluation, 'b')
            ax.plot(x_axis[tmp_fwhm_idx], transmission[tmp_fwhm_idx], 'ro')
            #     ax.set_ylim([np.min(transmission)-1,np.max(transmission)])
            #     ax.set_xlim([x_axis[0],x_axis[-1]])
            ax.set_title(sample)

        return max_value, fwhm

    def plot_sample(self,sample,ax=None):
        if ax is None:
            ax = plt.axes()

        ax.plot(self.get_wavelength(sample),self.get_cross_section(sample),label=sample)

        return ax

    def find_peak(self,sample):
        cross_section = self.get_cross_section(sample)
        wavelength = self.get_wavelength(sample)
        index_of_max = np.argmax(cross_section)
        return wavelength[index_of_max], cross_section[index_of_max], index_of_max

    @staticmethod
    def _convert_wavelength_to_energy(wavelength):
        return (sc.h * sc.c / (wavelength * 1e-9 * sc.e))  # in eV

    @staticmethod
    def _find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    @staticmethod
    def _create_x_y_trace(x, y, name):
        return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title='', energy=False):
        return go.Layout(
                title = title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='Scattering cross section [m<sup>2</sup>]'
                )
            )
