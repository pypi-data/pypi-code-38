import numpy as np
import matplotlib.pyplot as plt
from .flow_reactor_file_reader import FlowReactorFileReader


class FlowReactor:

    def __init__(self, filename=None,gridfs=None):
        if filename is not None:
            self.filename = filename
            data = FlowReactorFileReader.read_data_from_file(filename)
        elif gridfs is not None:
            self.filename = 'gridfs'
            data = FlowReactorFileReader.read_data_from_gridfs(gridfs)
        else:
            print("Provide filename or database handle")
            return
        self.start_time = data['start time']
        self.gases = data['gases']
        self.gas_concentrations = data['gas concentrations']
        self.mfcs = data['mfcs']
        self.max_flow_rates = data['max flow rates']
        self.k_factors = data['k factors']
        self.set_values = data['set values']
        self.measured_values = data['measured values']

    def plot_flow_rate(self,mfc):
        if mfc not in self.mfcs:
            raise ValueError(mfc + ' does not exist in file: ' + self.filename)
        x = self.measured_values['Time']
        y = self.measured_values['Flow Rate'][mfc]
        return plt.plot(x,y)

    def plot_reactor_temperature(self, ax=None):
        if ax is None:
            ax = plt.axes()
        x = self.measured_values['Time']
        y = self.measured_values['Temperature']['Reactor']

        ax.plot(x, y)
        return ax

    def plot_sample_temperature(self,ax=None):
        if ax is None:
            ax = plt.axes()
        x = self.measured_values['Time']
        y = self.measured_values['Temperature']['Sample']
        ax.plot(x,y)
        return ax

    @property
    def time(self):
        time = self.measured_values['Time']
        return np.array(time)

    @property
    def reactor_temperature(self):
        reactor_temperature = self.measured_values['Temperature']['Reactor']
        return np.array(reactor_temperature)

    @property
    def sample_temperature(self):
        sample_temperature = self.measured_values['Temperature']['Sample']
        return np.array(sample_temperature)

    def get_sample_temperature_at_time(self,time):
        index = FlowReactor._find_index_of_nearest(self.time,time)
        return self.sample_temperature[index]

    def shift_start_time_back(self,time):
        self.start_time = self.start_time - time
        for index in len(0,self.set_values['Time']):
            self.set_values['Time'][index] += time

        for index in len(0,self.measured_values['Time']):
            self.measured_values['Time'][index] += time

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(array - value)).argmin()
