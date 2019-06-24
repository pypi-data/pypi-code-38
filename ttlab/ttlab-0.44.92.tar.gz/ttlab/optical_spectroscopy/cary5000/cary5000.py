from .cary5000_file_reader import  Cary5000FileReader
from plotly.offline import init_notebook_mode, iplot, plot
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy import constants as sc
from scipy.interpolate import interp1d


class Cary5000:

    def __init__(self, filename=None,gridfs=None,johan_version=False,absorption=False,**kwargs):
        self.filename = filename
        if johan_version:
            self.version = 'johan'
            self.data = Cary5000FileReader.read_data_from_file(filename)
            print(self.data)
        elif filename:
            self.version = 'cool'
            self.absorption = absorption
            self.data = Cary5000FileReader.read_data(filename=self.filename,**kwargs)
        elif gridfs:
            self.version = 'johan'
            self.data = Cary5000FileReader.read_data_from_gridfs(gridfs)

    def get_wavelength(self, sample):
        if self.version == 'johan':
            return self.data['acquired data'][sample]['Wavelength (nm)']
        return self.data[sample].wavelength

    def get_transmission(self, sample):
        if self.version == 'johan':
            return self.data['acquired data'][sample]['%T']
        return self.data[sample].transmission

    def get_energy(self,sample):
        if self.version == 'johan':
            return 'wir müssen die Versionen wieder abschaffen'
        if self.data[sample].energy is None:
            self.data[sample].energy=self._convert_wavelength_to_energy(self.get_wavelength(sample))

        return self.data[sample].energy

    @property
    def is_absorption(self):
        return self.absorption

    @property
    def samples(self):
        if self.version == 'johan':
            return self.data['sample names']
        else:
            return self.data.keys()

    def get_area_under_curve(self,sample,interval):
        transmi = 100 - self.get_transmission(sample)
        wavelength = self.get_wavelength(sample)
        _, start_idx = self._find_nearest(wavelength, interval[1])
        _, end_idx = self._find_nearest(wavelength, interval[0])
        return np.trapz(transmi[start_idx:end_idx], wavelength[start_idx:end_idx])

    def get_fwhm_and_max(self,sample,range=50, show_fit=False, energy=True, fit_order=50, only_max=False):
        coordinate_zero = 100

        if energy:
            x_axis = self.get_energy(sample)
        else:
            print('Not yet implemented')
            return

        transmission = self.get_transmission(sample)

        ## get close area around maxium to fit
        max_rough_idx = np.argmin(transmission)
        transmission_narrow_max = transmission[max_rough_idx-range:max_rough_idx+range]
        x_axis_narrow_max = x_axis[max_rough_idx-range:max_rough_idx+range]

        ## fit around maximum to get a better (closer) value for the maximum/minimum
        polyfit_max = np.polyfit(x_axis_narrow_max, transmission_narrow_max, fit_order)
        poly1d_max = np.poly1d(polyfit_max)
        x_axis_max_evaluation = np.linspace(x_axis_narrow_max[0], x_axis_narrow_max[-1], 10000)
        transmission_max_evaluation = []
        for x in x_axis_max_evaluation:
            transmission_max_evaluation.append(poly1d_max(x))
        transmission_max_evaluation = np.array(transmission_max_evaluation)
        max_evaluation_idx = np.argmin(transmission_max_evaluation)
        max_value = x_axis_max_evaluation[max_evaluation_idx]
        fwhm=0
        if not only_max:
            ## determine closest point to the left of fwhm
            fwhm_hline = coordinate_zero-(coordinate_zero-transmission_max_evaluation[max_evaluation_idx])/2
            tmp_fwhm, tmp_fwhm_idx = self._find_nearest(transmission[:max_rough_idx], fwhm_hline)
            transmission_narrow_fwhm = transmission[tmp_fwhm_idx-range:tmp_fwhm_idx+range]
            x_axis_narrow_fwhm = x_axis[tmp_fwhm_idx-range:tmp_fwhm_idx+range]

            ## fit around this fwhm point to get a better (closer) value for it
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
            fig,ax = plt.subplots()
            ax.plot(x_axis,transmission,'x')
            ax.plot(x_axis_narrow_max,transmission_narrow_max,'o')
            ax.plot(x_axis_narrow_max,poly1d_max(x_axis_narrow_max))
            ax.axvline(max_value)
            ax.plot(x_axis_max_evaluation, transmission_max_evaluation, 'k')
            ax.set_ylim([np.min(transmission) - 1, np.max(transmission)])
            ax.set_xlim([x_axis[0], x_axis[-1]])
            ax.set_title(sample)
            if not only_max:
                ax.axhline(fwhm_hline)
                ax.plot(x_axis_fwhm_evaluation, transmission_fwhm_evaluation, 'b')
                ax.plot(x_axis[tmp_fwhm_idx], transmission[tmp_fwhm_idx], 'ro')
        return max_value, fwhm


    def get_weird_energy_like_stuff_under(self,sample,energy_interval):
        if self.version == 'johan':
            return 'das mit den verschiedenen Versionen ist irgendwie blöd'
        transmi = 100-self.get_transmission(sample)
        energy_axis = self.get_energy(sample)
        _, start_idx = self._find_nearest(energy_axis, energy_interval[0])
        _, end_idx = self._find_nearest(energy_axis, energy_interval[1])
        return np.sum(np.multiply(transmi[start_idx:end_idx], energy_axis[start_idx:end_idx]))


    def correct_offset(self):
        samples = self.samples

        for sample in samples:
            if samples == 'Baseline 100%T':
                continue
            trans = self.get_transmission(sample=sample)
            trans = trans + 100- max(trans)
            self.data[sample].transmission = trans
        return

    def correct_step(self,find_step_range=[200,1200], slope_correction=False):
        samples = self.samples

        for sample in samples:
            if sample == 'Baseline 100%T':
                continue

            wave = self.get_wavelength(sample=sample)

            trans = Cary5000._correct_step(wavelength=wave,transmission=self.get_transmission(sample=sample), find_step_range=find_step_range)

            if slope_correction is True:
                trans = Cary5000._correct_slope(wave, trans)
            self.data[sample].transmission = trans

        return

    def plotly_all(self, title='',energy=False ,mode='transmission'):
        init_notebook_mode(connected=True)
        data = []
        for sample in self.samples:
            if sample == 'Baseline':
                continue
            if energy:
                x = self.get_energy(sample)
            else:
                x = self.data[sample].wavelength
            y = self.data[sample].transmission
            if mode=='Arturo':
                trace = Cary5000._create_x_y_trace(x, 100-y, sample)
            else:
                trace = Cary5000._create_x_y_trace(x, y, sample)
            data.append(trace)
        layout = Cary5000._get_plotly_layout(title, mode=mode)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def plot_sample(self,sample,energy=False,ax=None):
        if ax is None:
            ax = plt.axes()

        if energy:
            x=self.get_energy(sample)
        else:
            x=self.get_wavelength(sample)

        ax.plot(x,self.get_transmission(sample),label=sample)
        return ax

    def find_peak(self,sample):
        transmission = self.get_transmission(sample)
        wavelength = self.get_wavelength(sample)
        index_of_min = np.argmin(transmission)
        return wavelength[index_of_min], transmission[index_of_min], index_of_min

    @staticmethod
    def _find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    @staticmethod
    def _correct_step(wavelength, transmission,find_step_range):

        start = find_step_range[1]
        end = find_step_range[0]

        start, start_idx= Cary5000._find_nearest(wavelength,start)
        end, end_idx= Cary5000._find_nearest(wavelength,end)

        grad = np.gradient(transmission, wavelength)
        gmid = np.argmax(abs(grad[start_idx:end_idx]))  + start_idx

        delta1 = transmission[gmid - 1] - transmission[gmid]
        delta2 = transmission[gmid] - transmission[gmid + 1]

        if abs(delta1) > abs(delta2):
            delta = delta1
            for i, t in enumerate(transmission):
                if i < gmid:
                    transmission[i] = transmission[i] - delta
        else:
            delta = delta2
            for i, t in enumerate(transmission):
                if i <= gmid:
                    transmission[i] = transmission[i] - delta

        return transmission

    @staticmethod
    def _correct_slope(wavelength, transmission):
        x = [wavelength[0], wavelength[-1]]
        y = [transmission[0], transmission[-1]]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        y_delta = intercept - 100 + slope * wavelength
        return transmission - y_delta

    @staticmethod
    def _convert_wavelength_to_energy(wavelength):
        return (sc.h * sc.c / (wavelength*1e-9 * sc.e)) # in eV

    @staticmethod
    def _create_x_y_trace(x, y, name):
        if name == 'Baseline 100%T':
            return go.Scatter(x=x, y=y, name=name, visible='legendonly')
        else:
            return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title='', mode='transmission'):
        if mode=='transmission':
            return go.Layout(
                title = title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='%T'
                )
            )
        else:
            return go.Layout(
                title=title,
                xaxis=dict(
                    title='Wavelength [nm]'
                ),
                yaxis=dict(
                    title='extinction'
                )
            )

