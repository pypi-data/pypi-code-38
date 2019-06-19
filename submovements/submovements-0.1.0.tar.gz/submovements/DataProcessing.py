import attr
from glob import glob
import os
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter, hilbert
import numpy as np

@attr.s
class Trial(object):

    ###
    # Trial(i,j) represents data from repetition i from block j
    # Using the preprocessor we can stream data from a directory and create trials
    # Using the preprocessor we can preprocess the trial position data into filtered velocity
    ###

    block = attr.ib(default=0)
    rep = attr.ib(default=0)
    stimulus = attr.ib(default='')
    position_data = attr.ib(default=None)
    velocity_data = attr.ib(default=None)
    filtered_velocity_data = attr.ib(default=None)
    #time = attr.ib(default=None)
    events = attr.ib(default=None)
    raw_file_path = attr.ib(default='')

    def __str__(self):
        return f'Block/Repetition: {self.block}/{self.rep}\n' \
            f'Stimulus: {self.stimulus}\n' \
            f'Raw data path: {self.raw_file_path}\n'

    def preprocess(self, preprocessor, axes=('x','y','z'), sg_win_len = 17, sg_polyorder=4, threshold=0.005):
        filtered_velocity = preprocessor.filter_raw_data(self.position_data[list(axes)],
                                                  window_len=sg_win_len,
                                                  polyorder=sg_polyorder,
                                                  deriv=1)
        filtered_velocity = preprocessor.remove_baseline(filtered_velocity, threshold=threshold)

        self.filtered_velocity_data = filtered_velocity

@attr.s
class Preprocessor(object):
    raw_paths = attr.ib(default='data')
    database_file_path = attr.ib(default='data\\database.mat')
    sample_rate = attr.ib(default=240)
    raw_headers = attr.ib(default=['SampleNum', 'x', 'y', 'z', 'phi', 'theta', 'psi', 'Time', 'Event'])

    def load_df_from_directory_gen(self, dir_path):
        ###
        # This is a generator which takes csv files from dir_path and yields Trials.
        ###

        self.raw_paths = glob(os.path.join(dir_path, '*.csv'))
        trial_out = Trial()
        for fn in self.raw_paths:
            try:
                df = pd.read_csv(fn, names=self.raw_headers)
                df = df.set_index('Time')
                trial_out.position_data = df[['x','y','z']]
                #trial_out.time = df[['Time']]
                trial_out.events = df[['Event']]
                trial_out.velocity_data = df[['x','y','z']].diff()
                trial_data = os.path.split(fn)[1].split(sep='_')
                trial_out.subject_id = trial_data[0]
                trial_out.stimulus = trial_data[1] + '_' + trial_data[2]
                trial_out.block = int(trial_data[3])
                trial_out.rep = int(os.path.splitext(trial_data[4])[0])
                trial_out.raw_file_path = fn
                yield trial_out
            except IOError:
                print(f'{fn} was not loaded.')
                continue

    def load_single_file(self, file_path):
        ###
        # This method loads a single csv and yields a single Trial
        ###

        trial_out = Trial()
        try:
            trial_out.data = pd.read_csv(file_path, names=self.raw_headers)
            trial_data = os.path.split(file_path)[1].split(sep='_')
            trial_out.subject_id = trial_data[0]
            trial_out.stimulus = trial_data[1]
            trial_out.raw_file_path = file_path
            return trial_out
        except IOError:
            raise AssertionError(f'{file_path} was not loaded.')

    def plot(self, data_in: pd.DataFrame, mode='pandas', sample_factor: int = 10):

        ###
        # This is a plotting method that will work on a given DataFrame
        # mode = 'pandas' will plot using Pandas and matplotlib.
        # mode = 'bokeh' will plot using bokeh.
        # sample_factor dictates how many samples will be displayed (lower -> higher performance -> lower resolution).
        ###

        if mode=='pandas':
            plt.figure()
            data_in.plot()
            plt.show()

        elif mode=='bokeh':
            sample = data_in.sample(sample_factor)
            source = ColumnDataSource(sample)
            f = figure()
            f.line(x='Time', y='x', color='red', source=source)
            f.line(x='Time', y='y', color='blue', source=source)
            show(f)
        else:
            print(f'Mode {mode} is not supported.')
            return None


    def filter_raw_data(self, data_in:pd.DataFrame, window_len=9, deriv=1, polyorder=4):
        ###
        # This method applies the Savitsky-Golay filter on a data frame.
        # For example, the velocity is extracted by setting deriv=1 and data_in to position data.
        #
        # S-G paramters:
        # window_len - how many samples are used for polynomial fitting of order polyorder.
        # deriv=n controls whether we smooth the data or its n'th derivative.
        ###

        df = data_in.copy()
        #df = pd.concat([data_in, time_vec], axis=1)
        #df = df.copy().set_index('Time')
        dx = df.index[1]

        # we start by filling NaNs in the data
        df = df.fillna(method='bfill')
        # we now apply a Savitzky-Golay filter to smooth the data
        for col in df:
            df[col] = savgol_filter(x=df[col],
                                    window_length=window_len,
                                    polyorder=polyorder,
                                    deriv=deriv,
                                    delta=dx)
        return df

    def remove_baseline(self, data_in:pd.DataFrame, threshold=0.005):
        ### TODO: check if we need to filter out baseline data --after-- the motion...
        # This method takes a data frame of velocity data, calculates the normalized magnitude of
        # tangential velocity and filters out any data that's lower than a given threshold.
        ###

        # calculate absolute velocity
        df = np.power(data_in, 2)
        df = df.sum(axis=1)

        #min-max normalization
        df = (df - df.min()) / (df.max() - df.min())


        #adaptive threshold
        #df_fast = df.rolling(window=int(self.sample_rate/2)).std()
        #df_slow = df.rolling(window=int(self.sample_rate)).std()
        #threshold = np.abs(df_fast-df_slow)

        return data_in.copy()[df >= threshold]

    def save_as_mat(self, data_in:pd.DataFrame, destination):
        ### TODO
        # Method to export a dataframe
        ###

        self.database_file_path = destination


        pass


