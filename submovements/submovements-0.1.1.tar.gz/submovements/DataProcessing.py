import attr
from glob import glob
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt
from pathlib import Path
import seaborn as sns

sns.set()


@attr.s
class Subject(object):
    id = attr.ib(init=False)
    df_dict = attr.ib({'square_left': [], 'square_right': [], 'tri_left': [], 'tri_right': []})
    dir_path = attr.ib(default='')
    df_folder = attr.ib(default='')

    def __attrs_post_init__(self):
        self.id = os.path.split(self.dir_path)[1]

    def create_total_df(self):
        self.df_total = pd.DataFrame({'Vx': [], 'Vy': [], 'Rep': [], 'Block': [], 'Time': [], 'Condition': [],
                                      'ID': [], 'pos x': [],
                                      'pos y': []})  # creating an empty array for concatination use later
        pproc = Preprocessor()
        trial_gen = pproc.load_df_from_directory_gen(self.dir_path)
        for trial in trial_gen:
            trial.preprocess(pproc)
            df = trial.create_df()
            trial.save_df(df, self.df_folder)
            for key in self.df_dict:
                if key == trial.stimulus:
                    self.df_dict[key].append(df)
            self.df_total = pd.concat([self.df_total, df])
        self.df_total = self.df_total.set_index(['ID', 'Condition', 'Block', 'Rep', 'Time']).sort_values(
            ['ID', 'Condition', 'Block', 'Rep'], ascending=True)

    def stimuli_plot_vx(self, num_of_trials):
        fig, axes = plt.subplots(2, 2)  # add name to subplots
        plt.xlabel('Time (sec)')
        plt.ylabel('Vx (cm/sec)')
        for n, key in enumerate(self.df_dict):
            if n == 0:
                axes[0, 0].set_title(key)
            if n == 1:
                axes[0, 1].set_title(key)
            if n == 2:
                axes[1, 0].set_title(key)
            if n == 3:
                axes[1, 1].set_title(key)
            for trial in range(num_of_trials):
                if n == 0:
                    sns.lineplot(x="Time", y="Vx", data=self.df_dict[key][trial], ax=axes[0, 0])
                if n == 1:
                    sns.lineplot(x="Time", y="Vx", data=self.df_dict[key][trial], ax=axes[0, 1])
                if n == 2:
                    sns.lineplot(x="Time", y="Vx", data=self.df_dict[key][trial], ax=axes[1, 0])
                if n == 3:
                    sns.lineplot(x="Time", y="Vx", data=self.df_dict[key][trial], ax=axes[1, 1])
        plt.show()

    def stimuli_plot_vy(self, num_of_trials):
        fig, axes = plt.subplots(2, 2)  # add name to subplots
        plt.xlabel('Time (sec)')
        plt.ylabel('Vy (cm/sec)')
        for n, key in enumerate(self.df_dict):
            if n == 0:
                axes[0, 0].set_title(key)
            if n == 1:
                axes[0, 1].set_title(key)
            if n == 2:
                axes[1, 0].set_title(key)
            if n == 3:
                axes[1, 1].set_title(key)
            for trial in range(num_of_trials):
                if n == 0:
                    sns.lineplot(x="Time", y="Vy", data=self.df_dict[key][trial], ax=axes[0, 0])
                if n == 1:
                    sns.lineplot(x="Time", y="Vy", data=self.df_dict[key][trial], ax=axes[0, 1])
                if n == 2:
                    sns.lineplot(x="Time", y="Vy", data=self.df_dict[key][trial], ax=axes[1, 0])
                if n == 3:
                    sns.lineplot(x="Time", y="Vy", data=self.df_dict[key][trial], ax=axes[1, 1])
        plt.show()


@attr.s
class Trial():
    ###
    # Trial(i,j) represents data from repetition i and block j
    # Using the preprocessor we can stream data from a
    # directory and create trials.
    # Using the preprocessor we can preprocess the trial
    # position data into filtered velocity
    ###

    block = attr.ib(default=0)          # Trial block
    rep = attr.ib(default=0)            # Trial repetition
    stimulus = attr.ib(default='')      # Trial stimulus
    raw_file_path = attr.ib(default='') # Path to trial raw data
    id = attr.ib(default='')            # Subject ID (number)

    # Data DataFrame which contains Position vectors and Velocity vectors.
    # We can choose which vectors to include from ('x','y','z') by using
    # the cols parameter. For example, cols=('x','y') will choose only dimensions x and y.

    data = attr.ib(default='')

    def preprocess(self, preprocessor,
                   cols=('x', 'y'),
                   threshold=0.05):
        ###
        # This method does Trial preprocessing using a Preprocessor
        # in directions chosen by cols.
        # Threshold refers to baseline removal. Data where ||Velocity|| < threshold
        # is removed. Threshold is given in percentage w.r.t to max(||Velocity||).
        ###

        assert isinstance(preprocessor, Preprocessor)

        cols=list(cols)
        self.data[cols] = preprocessor.filter_raw_data(self.data[cols])

        velocity_cols = [f'V{q}' for q in cols]
        self.data[velocity_cols] = preprocessor.sample_rate * \
                                             self.data[cols].diff().fillna(method='bfill')

        self.data = preprocessor.remove_baseline(self.data, cols=velocity_cols, threshold=threshold)

        self.data = self.data.set_index(self.data['Time']-self.data['Time'][0])

    def create_df(self):
        ###
        # Creates a DataFrame for every trial with the columns:
        # Vx, Vy, Condition, Time, ID, Block, Repetition
        # TODO: Generalize to z axis
        ###
        
        pos_x = self.data['x']
        pos_y = self.data['y']
        vx = self.data['Vx']
        vy = self.data['Vy']
        time = self.data.index.values
        condition = np.full(shape=len(vx), fill_value=self.stimulus)
        id = np.full(shape=len(vx),
                     fill_value=self.id
                     )
        block = np.full(shape=len(vx), fill_value=self.block, dtype=np.int)
        rep = np.full(shape=len(vx), fill_value=self.rep, dtype=np.int)
        return pd.DataFrame({'Vx': vx, 'Vy': vy, 'Rep': rep, 'Block': block,
                             'Time': time, 'Condition': condition, 'ID': id, 'pos x': pos_x, 'pos y': pos_y})

    def save_df(self, df, dest_folder):
        ###
        # Save recived data frame of the trial as a '_df.csv'
        ###

        if isinstance(df, pd.DataFrame):
            fname = f"{self.stimulus}_{self.block}_{self.rep}_df.csv"
            path = os.path.join(dest_folder, fname)
            if os.path.isdir(dest_folder):
                df.to_csv(path)
            else:
                try:
                    os.mkdir(dest_folder)
                    df.to_csv(path)
                except OSError:
                    print("Creation of the directory %s failed" % path)


@attr.s
class Preprocessor():
    ###
    # This is a Preprocessing entity which can filter,
    # cut-via-threshold and plot DataFrames
    ###

    raw_paths = attr.ib(default='data')  # Path list of all the raw data files
    sample_rate = attr.ib(default=240)  # Sample rate the raw data is sampled at

    raw_headers = attr.ib(default=['SampleNum', 'x', 'y', 'z',
                                   'phi', 'theta', 'psi', 'Time', 'Event'])

    def load_df_from_directory_gen(self, dir_path, cols=('x', 'y')):
        ###
        # This is a generator which takes csv
        # files from dir_path and yields Trials.
        # cols controls which dimensions are saved.
        ###

        assert Path(dir_path).is_dir(), \
            f'Destination directory does not exist ' \
            f'or is not a directory: {dir_path}'

        self.raw_paths = glob(str(Path(dir_path).joinpath('li_*_*_*_*.csv')))
        assert len(self.raw_paths) > 0, f'No source files found!'

        trial_out = Trial()
        trial_out.data = pd.DataFrame()
        cols = list(cols)
        for fn in self.raw_paths:
            try:
                df = pd.read_csv(fn, names=self.raw_headers)
                data = df['Time'].astype('float64')
                data = pd.concat([data, df[cols]], axis=1)
                trial_out.data = data
                trial_data = os.path.split(fn)[1].split(sep='_')
                trial_out.stimulus = trial_data[1] + '_' + trial_data[2]
                trial_out.block = int(trial_data[3])
                trial_out.rep = int(os.path.splitext(trial_data[4])[0])
                trial_out.raw_file_path = fn
                trial_out.id = os.path.split(dir_path)[1]
                yield trial_out
            except ValueError:
                raise AssertionError(f'Could not load {fn}.')

    def load_single_file(self, file_path, cols=('x', 'y')):
        ###
        # This method loads a single csv and yields a single Trial.
        # cols controls which dimensions are saved.
        ###

        assert Path(file_path).is_file(), f'File does not exists: {file_path}'
        file_path = Path(file_path)
        cols = list(cols)
        trial_out = Trial()
        try:
            df = pd.read_csv(file_path, names=self.raw_headers)
            data = df['Time'].astype('float64')
            data = pd.concat([data, df[cols]], axis=1)
            trial_out.data = data
            trial_data = os.path.split(file_path)[1].split(sep='_')
            trial_out.stimulus = trial_data[1] + '_' + trial_data[2]
            trial_out.block = int(trial_data[3])
            trial_out.rep = int(os.path.splitext(trial_data[4])[0])
            trial_out.raw_file_path = file_path
            trial_out.id = os.path.split(file_path)[1]
            return trial_out
        except ValueError:
            raise AssertionError(f'Could not load {file_path}.')

    @staticmethod
    def plot(data_in: pd.DataFrame):
        ###
        # This is a plotting method that will work on a given DataFrame.
        ###

        assert isinstance(data_in, pd.DataFrame)
        assert not data_in.empty, f'No data to plot!'

        plt.figure()
        data_in.plot()
        plt.show()

    @staticmethod
    def butter_lowpass(cutoff, fs, order):
        ###
        # fs - sample rate in S/s
        # order - filter order
        ###

        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        return butter(order, normal_cutoff, btype='low', analog=False)

    def butter_lowpass_filter(self, data, cutoff, fs, order=2):
        ###
        # cutoff - lowpass cutoff frequency in Hz
        # fs - sample rate in S/s
        # order - filter order.
        # Note: since we're using zero-phase filtering
        # the effective order is 2*order.
        # Here the effective order is 2*2=4 by default.
        ###

        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def filter_raw_data(self, data_in: pd.DataFrame, cutoff=5, order=2):
        ###
        # This method applies a 5hz low pass
        # zero-phase butterworth filter.
        ###

        assert isinstance(data_in, pd.DataFrame)
        assert not data_in.empty, f'No data to process!'

        df = data_in.copy()

        # we start by filling NaNs in the data using nearest neighbor.
        df = df.fillna(method='bfill')

        for col in df:
            df[col] = self.butter_lowpass_filter(df[col],
                                                 cutoff=cutoff,
                                                 fs=self.sample_rate,
                                                 order=order)
        return df

    def remove_baseline(self, data_in: pd.DataFrame, cols=('x', 'y'), threshold=0.05):
        ###
        # This method takes a data frame of velocity data,
        # calculates the normalized magnitude of
        # tangential velocity and filters out any data
        # that's lower than a given threshold.
        ###

        assert isinstance(data_in, pd.DataFrame)
        assert not data_in.empty, f'No data to process!'
        assert threshold > 0, f'Threshold must be greater or equal than zero.'
        assert len(cols) > 0, f'Cannot process if no columns are specified.'

        # calculate absolute velocity
        df = np.power(data_in[cols], 2)
        df = np.sqrt(df[cols].sum(axis=1))

        # min-max normalization
        df = (df - df.min()) / (df.max() - df.min())

        # find data above threshold
        idx = df.loc[df >= threshold]

        # expand data cutting limits

        low_cut_index = int(idx.index[0] - 0.1 * self.sample_rate \
                                if df.index.min() < idx.index[0] - 0.1 * self.sample_rate \
                                else df.index.min())
        high_cut_index = int(idx.index[-1] + 0.1 * self.sample_rate \
                                 if df.index.max() > idx.index[-1] + 0.1 * self.sample_rate \
                                 else df.index.max())

        return data_in.copy()[low_cut_index:high_cut_index].reset_index(drop=True)
