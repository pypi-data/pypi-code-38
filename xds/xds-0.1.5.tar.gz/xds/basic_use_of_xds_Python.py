# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:54:41 2019

@author: xuan
"""
import numpy as np
from xds import lab_data, list_to_nparray, smooth_binned_spikes
import matplotlib.pyplot as plt
"""
First, creating the 'lab_data' object from one MATLAB-xds file
In the IDE of Spyder, you can check the data easily.

"""
base_path = './'
file_name = 'Chewie_20131022_001.mat'
dataset = lab_data(base_path, file_name)
#%%
"""
Then, we can grab data from the 'lab_data' object. If you are using Spyder, you 
may directly see the variables in 'Variable explorer' on the right side.
"""

"""
We can do without trial information, and everything is NumPy array.
"""
time_frame = dataset.time_frame
bin_width = dataset.bin_width

# spike counts, using the bin width specific by bin_width
# each row is a sample, each colum is an electrode
spike_counts = dataset.spike_counts

# kinematics : position
kin_p = dataset.kin_p

# kinematics : velocity
kin_v = dataset.kin_v
"""
If there are EMG signals, they can be got using:
EMG = dataset.EMG
EMG_names = dataset.EMG_names
"""
if dataset.has_EMG == 1:
    EMG = dataset.EMG
    EMG_names = dataset.EMG_names
else:
    print('This file does not contrain EMG')  
    
"""
In Spyder, figures can be shown direcly inside the console window
"""
plt.figure()
plt.plot(time_frame[:1000], spike_counts[:1000, 23])
plt.figure()
plt.plot(time_frame[:1000], kin_p[:1000, 0])
plt.plot(time_frame[:1000], kin_v[:1000, 0])
if dataset.has_EMG == 1:
    plt.figure()
    plt.plot(time_frame[:1000], EMG[:1000, 4])
#%%
"""
We can also analyze the data with trial information. Now everything is 'list', 
but inside the list, it's still NumPy array
"""
# Each row of the list is a trial, 'R' means those are rewarded trials
# You can also explore aborted trials ('A') and failed trials ('F').
trial_spike_counts = dataset.get_trials_data_spike_counts('R', 'gocue_time', 0.5)

if dataset.has_EMG == 1:
    trial_EMG = dataset.get_trials_data_EMG('R')
    
trial_force = dataset.get_trials_data_force('R')

# Kinematics
trial_kin_p, trial_kin_v, trial_kin_a = dataset.get_trials_data_kin('R', 'gocue_time', 0.5)

# You can find target onset time, go cue time, target information for each tiral with this function
summary = dataset.get_trials_summary()

# Do some plotting using trial information
plt.figure(figsize = [5,5])
for i in range(len(trial_kin_p)):
    plt.plot(trial_kin_p[i][:, 0], trial_kin_p[i][:, 1], 'b')
plt.axis('off')  
#%%
"""
If you need to re-bin the data but need not to update the attributes in your 
'dataset' object, you can use the functions below. They return the re-binned
data, but don't change the attributes (e.g.They don't change dataset.spike_counts.)
"""
time_spike_counts, spike_counts = dataset.bin_spikes(0.02)
if dataset.has_EMG == 1:
    time_EMG, EMG = dataset.resample_EMG(0.02)
time_force, force = dataset.resample_force(0.02)
time_kin, kin_p, kin_v, kin_a = dataset.resample_kin(0.02)
"""
A 'non-member' function is also provided for gaussian smoothing
"""
smoothed = smooth_binned_spikes(spike_counts, 0.02, 'gaussian', 0.02)
#%%
"""
If you need to re-bin and also update the attributes in your 'dataset' object,
you just need to run the function below, without running the separate functions
above 
"""
dataset.update_bin_data(0.02)
"""
By running this, spikes, EMG, kinematics and forces are re-binned, and 
attributes including dataset.spike_counts, dataset.EMG, dataset.force, 
dataset.kin_p, dataset.kin_v, dataset.kin_a, dataset.time_frame, dataset.bin_width
are all changed.
"""
print(dataset.bin_width)
  
#%%
"""
You can save the 'lab_data' object above to a pickle file, if file_name is zero,
it will use the same name as the .mat file. If you specify the new file name, it
will use the file name you give.
"""
dataset.save_to_pickle('./', 'Chewie_20ms')

"""
When loading a pickle file, use the codes below
"""
import _pickle as pickle
with open ('./Chewie_20ms', 'rb') as fp:
    my_data = pickle.load(fp)
    
spike_counts = my_data.spike_counts 

#%%
"""
An example for showing how to use the data structure. Just for fun.
"""
from sklearn.decomposition import PCA

"""
Using the first 100 trials to fit
"""
train_data_spike_counts = trial_spike_counts[:100]
"""
But we need numpy arrays in training, so:
"""
train_data_spike_counts = list_to_nparray(train_data_spike_counts)
"""
Now the variable 'train_data_spike_counts' is a numpy array
"""
pca = PCA(n_components = 16)
pca.fit(train_data_spike_counts)

"""
Use 101th:150th tiral to test, calculate the transformed signals trial by trial
"""
test_data_spike_counts = trial_spike_counts[101:150]
pca_test_data_spike_counts = []
for i in range(len(test_data_spike_counts)):
    pca_test_data_spike_counts.append(pca.transform(test_data_spike_counts[i]))

"""
Plot them trial by trial
"""
plt.figure(figsize = [5,5])
for each in pca_test_data_spike_counts:
    plt.plot(each[:, 2], each[:, 1], 'b.')
plt.axis('off')  





