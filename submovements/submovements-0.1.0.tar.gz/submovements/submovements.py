# -*- coding: utf-8 -*-

from DataProcessing import Preprocessor, Trial

path_to_raw_data = '..\\data\\results\\simonvisual\\1'
path_to_database = '..\\data\\processed_data.mat'
sample_rate = 240 #S/s

pproc = Preprocessor()
raw_data_gen = pproc.load_df_from_directory_gen(dir_path=path_to_raw_data)


for trial in raw_data_gen:
    trial.preprocess(pproc, axes=['x','y'])
    pproc.plot(trial.velocity_data[['x', 'y']], mode='pandas')
    pproc.plot(trial.filtered_velocity_data[['x', 'y']], mode='pandas')

    print(1)
    break
