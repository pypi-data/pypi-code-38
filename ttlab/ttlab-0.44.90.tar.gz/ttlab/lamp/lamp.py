from .lamp_file_reader import LampFileReader, Data
import numpy as np


class Lamp:

    def __init__(self, filename, start_time=0):
        self.filename = filename
        self.data = LampFileReader.read_data(filename)
        self.data = Lamp._convert_raw_data(self.data, start_time) # inserts 0 element and creates relative time

    @property
    def absolute_time(self):
        return self.data.abs_time

    @property
    def relative_time(self):
        return self.data.rel_time

    @property
    def power(self):
        return self.data.power

    def add_light_to_plot(self,ax):
        t = self.rel_time
        for i, steps in enumerate(t):
            if i == 0:
                continue
            ax.axvline(t[i], color='grey', lw=0.5, alpha=0.2)
            if i % 2 == 0:
                ax.axvspan(t[i - 1], t[i], alpha=0.1, color='grey')
        return ax

    def add_light_power_to_plot(self,ax):
        ax.step(self.rel_time,self.power,'y', where='post')
        return ax


    @staticmethod
    def _convert_raw_data(data, start_time):

        data.power = np.insert(data.power,0,0,axis=0)
        data.rel_time = data.abs_time - start_time
        data.rel_time = np.insert(data.rel_time,0,0)

        return data