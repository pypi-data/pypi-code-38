from ..mass_spectrometer import MassSpectrometer
from ..flow_reactor import FlowReactor
from ..lamp import Lamp
from .X0_functions import X0Functions
import numpy as np
import matplotlib.pyplot as plt


class X0Reactor:

    def __init__(self, filename_ms=None, filename_fr=None, filename_light=None,gridfs_ms=None, gridfs_fr=None):
        if filename_ms is not None:
            self.MassSpectrometer = MassSpectrometer(filename=filename_ms)
        elif gridfs_ms is not None:
            self.MassSpectrometer = MassSpectrometer(gridfs=gridfs_ms)

        if filename_fr is not None:
            self.FlowReactor = FlowReactor(filename=filename_fr)
        elif gridfs_fr is not None:
            self.FlowReactor = FlowReactor(gridfs=gridfs_fr)

        if filename_light:
            self.Lamp = Lamp(filename=filename_light,start_time=self.FlowReactor.start_time)
        self._align_times()

    def plot_ms(self, gas, ax=None, color=None):
        return self.MassSpectrometer.plot(gas=gas, ax=ax, color=color)

    def plot_all_ms(self,ax=None):
        return self.MassSpectrometer.plot_all(ax)

    def plot_flow_rate(self, mfc):
        return self.FlowReactor.plot_flow_rate(mfc)

    def plot_reactor_temperature(self):
        return self.FlowReactor.plot_reactor_temperature()

    def plot_sample_temperature(self, ax=None):
        return self.FlowReactor.plot_sample_temperature(ax)

    def get_sample_temperature(self):
        return self.FlowReactor.sample_temperature

    @property
    def flow_reactor_time(self):
        return self.FlowReactor.time

    def get_ms_time(self,gas,range=None):
        return self.MassSpectrometer.get_time_relative(gas,range=range)

    def get_ion_current(self,gas,range=None):
        return self.MassSpectrometer.get_ion_current(gas,range=range)

    def get_ion_current_and_sample_temperature(self,gas,range=None):
        ion_current = self.get_ion_current(gas=gas,range=range)
        time = self.get_ms_time(gas=gas,range=range)
        temperature = self._get_sample_temperature_at_times(time_array=time)
        return ion_current, temperature

    def correct_for_drifting(self,correction_gas='Ar'):
        self.MassSpectrometer.correct_for_drifting(correction_gas=correction_gas)

    def calculate_activation_energy(self,time_intervals,gas,method='steps',boltzmann_constant = 0.0083144621):
        temperature = np.array([])
        ion_current = np.array([])
        if method is 'interval':
            for interval in time_intervals:
                    temperature = np.append(temperature,[self._get_average_sample_temperature_in_interval(interval)])
                    ion_current = np.append(ion_current,[self._get_average_ion_current_in_interval(interval,gas)])
        elif method is 'steps':
            for index,interval in enumerate(time_intervals):
                if index is 0:
                    temperature = np.append(temperature, [self.get_sample_temperature_at_time(interval[0])])
                    ion_current = np.append(ion_current, [self.get_ion_current_at_time(interval[0],gas)])
                else:
                    temperature = np.append(temperature, [temperature[index-1]+self._get_max_sample_temperature_difference_in_interval(interval)])
                    ion_current = np.append(ion_current, [ion_current[index-1]+self._get_max_ion_current_diff_in_interval(interval, gas)])
        else:
            raise ValueError('Method \'' + method + '\' does not exist. Choose either \'steps\' or \'interval\'')
        activation_energy, error, linear_fit, v = X0Functions.calculate_activation_energy(temperature=temperature, reaction_rate=ion_current, boltzmann_constant=boltzmann_constant)
        return activation_energy, temperature, ion_current, linear_fit, error, v

    def plot_activation_energy(self,time_intervals,gas,ax=None,method='steps'):
        activation_energy, temperature, ion_current, linear_fit, error,v  = self.calculate_activation_energy(time_intervals,gas,method)
        boltzmann_constant = 0.0083144621 # kj/(K*mol)
        temperature_fit = np.array([1/((temperature[0]+273)*boltzmann_constant), 1/((temperature[len(temperature)-1]+273)*boltzmann_constant)])
        ion_current_fit = temperature_fit*linear_fit[0] + linear_fit[1]
        if ax is None:
            ax = plt.axes()
        ax.plot(1/((temperature+273)*boltzmann_constant),np.log(ion_current),'o')
        ax.plot(temperature_fit,ion_current_fit, label=str(round(activation_energy,2)) + ' kJ/mol')
        ax.legend()
        return ax

    def get_sample_temperature_at_time(self,time):
        return self.FlowReactor.get_sample_temperature_at_time(time)

    def get_ion_current_at_time(self,time,gas):
        return self.MassSpectrometer.get_ion_current_at_time(time,gas)

    def _get_sample_temperature_at_times(self,time_array):
        temperature = []
        for time in time_array:
            temperature.append(self.get_sample_temperature_at_time(time))
        return np.array(temperature)

    def _get_average_sample_temperature_in_interval(self, interval):
        sample_temperature = self.get_sample_temperature()
        flow_reactor_time = self.get_flow_reactor_time()
        start_index = self._find_index_of_nearest(flow_reactor_time,interval[0])
        end_index = self._find_index_of_nearest(flow_reactor_time,interval[1])
        return np.mean(sample_temperature[start_index:end_index])

    def _get_average_ion_current_in_interval(self,interval,gas):
        ion_current = self.get_ion_current(gas)
        ms_time = self.get_ms_time(gas)
        start_index = self._find_index_of_nearest(ms_time,interval[0])
        end_index = self._find_index_of_nearest(ms_time,interval[1])
        return np.mean(ion_current[start_index:end_index])

    def _get_max_sample_temperature_difference_in_interval(self,interval):
        sample_temperature = self.get_sample_temperature()
        flow_reactor_time = self.flow_reactor_time
        start_index = self._find_index_of_nearest(flow_reactor_time, interval[0])
        end_index = self._find_index_of_nearest(flow_reactor_time, interval[1])
        return np.max(sample_temperature[start_index:end_index])-np.min(sample_temperature[start_index:end_index])

    def _get_max_ion_current_diff_in_interval(self, interval,gas):
        ion_current = self.get_ion_current(gas)
        ms_time = self.get_ms_time(gas)
        start_index = self._find_index_of_nearest(ms_time, interval[0])
        end_index = self._find_index_of_nearest(ms_time, interval[1])
        return np.max(ion_current[start_index:end_index])-np.min(ion_current[start_index:end_index])

    def _align_times(self):
        time_difference = self.MassSpectrometer.start_time - self.FlowReactor.start_time
        self.MassSpectrometer.shift_start_time_back(time_difference)

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()
