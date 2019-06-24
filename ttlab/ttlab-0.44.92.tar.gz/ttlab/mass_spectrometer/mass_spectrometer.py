import matplotlib.pyplot as plt
import numpy as np
from .mass_spectrometer_file_reader import MassSpectrometerFileReader
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot
import warnings


class MassSpectrometer:
    """ Mass spectrometer class for importing mass spectrometer data. Currently supports files from Quadera software.

        Attributes
        ----------
        filename: str, optional
            The path to the mass spec data file.
        gridfs: pymongo database handle, optional
            A pymongo Gridfs handle of the data file.
    """
    def __init__(self, filename=None,gridfs=None):
        if filename is not None:
            self.filename = filename
            self.data = MassSpectrometerFileReader.read_data_from_file(filename)
        elif gridfs is not None:
            self.filename = 'Gridfs'
            self.data = MassSpectrometerFileReader.read_data_from_gridfs(gridfs)
        else:
            print("Provide filename or database handle")
            return

        self.is_corrected_for_drifting = False

    @property
    def gases(self):
        """The measured gases"""
        return self.data['gases']

    @property
    def start_time(self):
        """The time the experiment started in unix time"""
        return self.data['start time']

    @start_time.setter
    def start_time(self, value):
        self.data['start time'] = value

    @property
    def end_time(self):
        """The time the experiment ended in unix time"""
        return self.data['end time']

    @end_time.setter
    def end_time(self, value):
        self.data['end time'] = value

    @property
    def acquired_data(self):
        return self.data['acquired data']

    def plot(self, gas, ax=None, color=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        x = self.acquired_data[gas]['Time Relative [s]']
        y = self.acquired_data[gas]['Ion Current [A]']

        if ax is None:
            ax = plt.axes()
        ax.plot(x, y, color=color)
        ax.set_yscale('log')
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Ion Current [A]')
        return ax

    def plot_all(self, ax=None):
        if ax is None:
            ax = plt.axes()
        for gas in self.gases:
            ax = self.plot(gas=gas,ax=ax)
        ax.legend(self.gases)
        return ax

    def get_ion_current(self, gas,range=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        ion_current = self.acquired_data[gas]['Ion Current [A]']
        if range:
            time = self.get_time_relative(gas)
            start_index = MassSpectrometer._find_index_of_nearest(time,range[0])
            end_index = MassSpectrometer._find_index_of_nearest(time,range[1])
            return np.array(ion_current[start_index:end_index])
        return np.array(ion_current)

    def get_time_relative(self, gas,range=None):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        time_relative = self.acquired_data[gas]['Time Relative [s]']
        if range:
            start_index = MassSpectrometer._find_index_of_nearest(time_relative,range[0])
            end_index = MassSpectrometer._find_index_of_nearest(time_relative,range[1])
            return np.array(time_relative[start_index:end_index])
        return np.array(time_relative)

    def get_time(self, gas):
        if gas not in self.gases:
            raise ValueError(gas + ' does not exist in file: ' + self.filename)
        return np.array(self.acquired_data[gas]['Time'])

    def shift_start_time_back(self, time):
        self.start_time = self.start_time - time
        self.end_time = self.end_time - time
        for gas in self.gases:
            for index in range(0, len(self.acquired_data[gas]['Time Relative [s]'])):
                self.acquired_data[gas]['Time Relative [s]'][index] = self.acquired_data[gas]['Time Relative [s]'][
                                                                          index] + time

    def plotly_all(self,title=''):
        init_notebook_mode(connected=True)
        data = []
        for gas in self.gases:
            x = self.acquired_data[gas]['Time Relative [s]']
            y = self.acquired_data[gas]['Ion Current [A]']
            trace = MassSpectrometer._create_x_y_trace(x, y, gas)
            data.append(trace)
        layout = MassSpectrometer._get_plotly_layout(title)
        fig = go.Figure(data=data, layout=layout)
        return iplot(fig)

    def correct_for_drifting(self,correction_gas='Ar'):
        if self.is_corrected_for_drifting:
            warnings.warn('Ion current is already corrected for drifting. No further correctrion was performed.')
            return
        correction_current = self.get_ion_current(correction_gas)
        mean_correction_current = np.mean(correction_current)
        for gas in self.gases:
            min_length =int(min(len(correction_current),len(self.acquired_data[gas]['Ion Current [A]'])))
            for n in range(0,min_length-1):
                self.acquired_data[gas]['Ion Current [A]'][n] = self.acquired_data[gas]['Ion Current [A]'][n]*mean_correction_current/correction_current[n]
        self.is_corrected_for_drifting = True

    def get_ion_current_at_time(self,time,gas):
        index = self._find_index_of_nearest(self.get_time_relative(gas),time)
        return self.get_ion_current(gas)[index]

    @staticmethod
    def _find_index_of_nearest(array, value):
        return (np.abs(np.array(array) - value)).argmin()

    @staticmethod
    def _create_x_y_trace(x, y, name):
        return go.Scatter(x=x, y=y, name=name)

    @staticmethod
    def _get_plotly_layout(title=''):
        return go.Layout(
            title=title,
            xaxis=dict(
                title='Time [s]',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                )
            ),
            yaxis=dict(
                title='Ion Current [A]',
                type='log',
                titlefont=dict(
                    family='Courier New, monospace',
                    size=18,
                    color='#7f7f7f'
                ),
                exponentformat='e',
                showexponent='all'
            )
        )
