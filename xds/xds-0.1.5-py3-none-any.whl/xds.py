# -*- coding: utf-8 -*-
"""
Created on Mon May 20 16:49:25 2019

@author: xuan
"""
import sys
import numpy as np
import scipy.io as sio
from scipy import stats

if sys.version[0] == '2':
    import cPickle as pickle
else:
    import _pickle as pickle
    


def list_to_nparray(X):
    n_col = np.size(X[0],1)
    Y = np.empty((0, n_col))
    for each in X:
        Y = np.vstack((Y, each))
    return Y

def smooth_binned_spikes(spike_counts, bin_width, kernel_type, kernel_SD, sqrt = 0):
    smoothed = []
    binned_spikes = spike_counts.T.tolist()
    if sqrt == 1:
       for (i, each) in enumerate(binned_spikes):
           binned_spikes[i] = np.sqrt(each)
    bin_size = bin_width
    kernel_hl = np.ceil( 3 * kernel_SD / bin_size )
    normalDistribution = stats.norm(0, kernel_SD)
    x = np.arange(-kernel_hl*bin_size, (kernel_hl+1)*bin_size, bin_size)
    kernel = normalDistribution.pdf(x)
    if kernel_type == 'gaussian':
        pass
    elif kernel_type == 'half_gaussian':
       for i in range(0, int(kernel_hl)):
            kernel[i] = 0
    n_sample = np.size(binned_spikes[0])
    nm = np.convolve(kernel, np.ones((n_sample))).T[int(kernel_hl):n_sample + int(kernel_hl)] 
    for each in binned_spikes:
        temp1 = np.convolve(kernel,each)
        temp2 = temp1[int(kernel_hl):n_sample + int(kernel_hl)]/nm
        smoothed.append(temp2)
    #print('The input spike counts have been smoothed.')
    return np.asarray(smoothed).T
    
class lab_data:
    def __init__(self, base_path, file_name):
        self.file_name = file_name[:-4]
        file_name = ''.join([base_path, file_name])
        print( file_name )
        self.parse_file(file_name)
        self.print_file_info()
        
    def parse_file(self, file_name):
        readin = sio.loadmat(file_name)
        xds = readin['xds']
        self.time_frame = xds['time_frame'][0][0]
        
        self.matlab_meta = xds['meta'][0][0]
        self.__meta = dict()
        self.__meta['monkey_name'] = self.matlab_meta[0][0]['monkey'][0]
        self.__meta['task_name'] = self.matlab_meta[0][0]['task'][0]
        self.__meta['duration'] = self.matlab_meta[0][0]['duration'][0]
        self.__meta['collect_date'] = self.matlab_meta[0][0]['dateTime'][0]
        self.__meta['raw_file_name'] = self.matlab_meta[0][0]['rawFileName'][0]
        self.__meta['array'] = self.matlab_meta[0][0]['array'][0]
        
        self.has_EMG = xds['has_EMG'][0][0][0]
        self.has_kin = xds['has_kin'][0][0][0]
        self.has_force = xds['has_force'][0][0][0]
        self.bin_width = xds['bin_width'][0][0][0]
        self.sorted = xds['sorted'][0][0][0]
        self.spike_counts = xds['spike_counts'][0][0]
        self.spikes = xds['spikes'][0][0][0].tolist()
        self.unit_names = []
        for each in xds['unit_names'][0][0][0].tolist():
            self.unit_names.append(each[0])
        
        if self.has_EMG == 1:
            self.EMG = xds['EMG'][0][0]
            self.EMG_names = []
            for each in xds['EMG_names'][0][0][0].tolist():
                self.EMG_names.append(each[0])
        if self.has_force == 1:
            self.force = xds['force'][0][0]
        if self.has_kin == 1:
            self.kin_p = xds['kin_p'][0][0]
            self.kin_v = xds['kin_v'][0][0]
            self.kin_a = xds['kin_a'][0][0]
            
        self.trial_target_corners = xds['trial_target_corners'][0][0]
        self.trial_target_dir = xds['trial_target_dir'][0][0]
        self.trial_result = xds['trial_result'][0][0]
        self.trial_start_time = xds['trial_start_time'][0][0]
        self.trial_end_time = xds['trial_end_time'][0][0]
        self.trial_gocue_time = xds['trial_gocue_time'][0][0]
        self.trial_info_table_header = []
        for each in xds['trial_info_table_header'][0][0].tolist():
            self.trial_info_table_header.append(each[0][0])
        self.trial_info_table = xds['trial_info_table'][0][0].tolist()
        
        
        self.n_neural = np.size(self.spike_counts, 1)
        if self.has_EMG == 1:
            self.n_EMG = np.size(self.EMG, 1)
        else:
            self.n_EMG = 0
        if self.has_force == 1:
            self.n_force = np.size(self.force, 1)
        else:
            self.n_force = 0
            
    def get_meta(self):
        a = dict()
        a = self.__meta
        return a
        
    def print_file_info(self):
        print('Monkey: %s' % (self.__meta['monkey_name']))
        print('Task: %s' % (self.__meta['task_name']))
        print('Collected on %s ' % (self.__meta['collect_date']))
        print('Raw file name is %s' % (self.__meta['raw_file_name']))
        print('The array is in %s' % (self.__meta['array']))
        print('There are %d neural channels' % (self.n_neural))
        print('Sorted? %d' % (self.sorted))
        print('There are %d EMG channels' % (self.n_EMG))
        print('Current bin width is %.4f seconds' % (self.bin_width))
        if self.has_EMG == 1:
            print('The name of each EMG channel:')
            for i in range(len(self.EMG_names)):
                print(self.EMG_names[i])
        print('The dataset lasts %.4f seconds' % (self.__meta['duration']))
        print('There are %d trials' % (len(self.trial_result)))
        print('In %d trials the monkey got reward' % (len(np.where(self.trial_result == 'R')[0])))
    
    def print_trial_info_table_header(self):
        for each in self.trial_info_table_header:
            print(each)
            
    def get_one_colum_in_trial_info_table(self, colum_name):
        n = np.where(np.asarray(self.trial_info_table_header) == colum_name)[0][0]
        a = []
        for each in self.trial_info_table:
            a.append(each[n][0][0])
        return a
    
    def save_to_pickle(self, path, file_name = 0):
        if file_name == 0:
            f = ''.join((path, self.file_name))
        else:
            f = ''.join((path, file_name))
        with open (f, 'wb') as fp:
            pickle.dump(self, fp)
        print('Save to %s successfully' %(f))
        
    def get_trials_idx(self, my_type, trial_start, time_ahead):
        """ my_type: 'R', 'A', 'F' """
        """ 'R' for reward """
        """ 'A' for aborted """
        """ 'F' for failed """
        trials_idx = []
        if trial_start == 'start_time':
            my_T = self.trial_start_time
        elif trial_start == 'gocue_time':
            my_T = self.trial_gocue_time
      
        temp = np.where(self.trial_result == my_type)[0]
        if len(temp) != 0:
           for n in temp:
               if np.isnan(self.trial_end_time[n]) == False:
                   if np.isnan(my_T[n]) == False:
                       ind = np.where((self.time_frame > my_T[n] - time_ahead) & (self.time_frame < self.trial_end_time[n]))[0]
                       trials_idx.append(ind)
        return trials_idx
    
    def get_trials_data_spike_counts(self, my_type = 'R', trial_start = 'start_time', time_ahead = 0):
        trial_spike_counts = []
        ind = self.get_trials_idx(my_type, trial_start, time_ahead)
        for n in ind:
            a = self.spike_counts[n, :]
            trial_spike_counts.append(a)
        return trial_spike_counts
    
    def get_trials_data_time_frame(self, my_type = 'R', trial_start = 'start_time', time_ahead = 0):
        trial_time_frame = []
        ind = self.get_trials_idx(my_type, trial_start, time_ahead)
        for n in ind:
            a = self.time_frame[n, :]
            trial_time_frame.append(a)
        return trial_time_frame

    def get_trials_data_EMG(self, my_type = 'R', trial_start = 'start_time', time_ahead = 0):
        if self.has_EMG == 0:
            print('There is no EMG in this file')
            return 0
        else:
            trial_EMG = []
            ind = self.get_trials_idx(my_type, trial_start, time_ahead)
            for n in ind:
                a = self.EMG[n, :]
                trial_EMG.append(a)
            return trial_EMG
        
    def get_trials_data_force(self, my_type = 'R', trial_start = 'start_time', time_ahead = 0):
        if self.has_force == 0:
            print('There is no force in this file')
            return 0
        else:
            trial_force = []
            ind = self.get_trials_idx(my_type, trial_start, time_ahead)
            for n in ind:
                a = self.force[n, :]
                trial_force.append(a)
            return trial_force
            
    def get_trials_data_kin(self, my_type = 'R', trial_start = 'start_time', time_ahead = 0):
        if self.has_kin == 0:
            print('There is no kinematics in this file')
            return 0
        else:
            trial_kin_p = []
            trial_kin_v = []
            trial_kin_a = []
            ind = self.get_trials_idx(my_type, trial_start, time_ahead)
            for n in ind:
                a = self.kin_p[n, :]
                trial_kin_p.append(a)
                b = self.kin_v[n, :]
                trial_kin_v.append(b)
                c = self.kin_a[n, :]
                trial_kin_a.append(c)
            return trial_kin_p, trial_kin_v, trial_kin_a
        
    def get_trials_summary(self, my_type = 'R'):
        trials_summary = dict()
        trials_summary['trial_type'] = my_type
        temp = np.where(self.trial_result == my_type)[0]
        if len(temp) != 0:
            a = [[], [], [], [], []]
            for i in range(len(temp)):
                a[0].append(self.trial_start_time[temp[i]])
                a[1].append(self.trial_end_time[temp[i]])
                a[2].append(self.trial_gocue_time[temp[i]])
                a[3].append(self.trial_target_corners[temp[i]])
                a[4].append(self.trial_target_dir[temp[i]])
            trials_summary['trial_start_time'] = np.asarray(a[0])
            trials_summary['trial_end_time'] = np.asarray(a[1])
            trials_summary['gocue_time'] = np.asarray(a[2])
            trials_summary['tgt_corners'] = np.asarray(a[3])
            trials_summary['tgt_dir'] = np.asarray(a[4])    
        return trials_summary
        
    def update_bin_data(self, bin_size, update = 1):
        t_spike, spike_counts = self.bin_spikes(bin_size)
        if self.has_EMG == 1:
            t_EMG, EMG = self.resample_EMG(bin_size)
            if len(t_EMG) > len(t_spike):
                EMG = EMG[:len(t_spike), :]
        if self.has_force == 1:
            t_force, force = self.resample_force(bin_size)
            if len(t_force) > len(t_spike):
                force = force[:len(t_spike), :]
        if self.has_kin == 1:
            t_kin, kin_p, kin_v, kin_a = self.resample_kin(bin_size)
            if len(t_kin) > len(t_spike):
                kin_p = kin_p[:len(t_spike), :]
                kin_v = kin_v[:len(t_spike), :]
                kin_a = kin_a[:len(t_spike), :]
        
        if update == 1:
            self.time_frame = t_spike
            self.bin_width = bin_size
            self.spike_counts = spike_counts
            if self.has_EMG == 1:
                self.EMG = EMG
            if self.has_force == 1:
                self.force = force
            if self.has_kin == 1:
                self.kin_p = kin_p
                self.kin_v = kin_v
                self.kin_a = kin_a
    
    def bin_spikes(self, bin_size):
        print('The new bin width is %.4f s' % (bin_size)) 
        spike_counts = [] 
        bins = np.arange(self.time_frame[0], self.time_frame[-1], bin_size)
        bins = bins.reshape((len(bins),))
        for each in self.spikes:
            bb=each.reshape((len(each),))
            out, _ = np.histogram(bb, bins)
            spike_counts.append(out)
        bins = bins.reshape((len(bins),1))
        return bins[1:], np.asarray(spike_counts).T
              
    def resample_EMG(self, bin_size):
        if self.has_EMG == 0:
            print('There is no EMG in this file.')
            return 0
        else:
            if bin_size < self.bin_width:
                print('Cannot bin EMG using this bin size')
                return 0
            else:
                down_sampled = []
                t = []
                n = bin_size/self.bin_width
                length = int(np.floor(np.size(self.EMG, 0)/n))
                for i in range(1, length):
                    down_sampled.append(self.EMG[int(np.floor(i*n)),:])
                    t.append(self.time_frame[int(np.floor(i*n))])
                down_sampled = np.asarray(down_sampled)
                t = np.asarray(t)
                return t, down_sampled

    def resample_force(self, bin_size):
        if self.has_force == 0:
            print('There is no force in this file.')
            return 0
        else:
            if bin_size < self.bin_width:
                print('Cannot bin force using this bin size')
                return 0
            else:
                down_sampled = []
                t = []
                n = bin_size/self.bin_width
                length = int(np.floor(np.size(self.force, 0)/n))
                for i in range(1, length):
                    down_sampled.append(self.force[int(np.floor(i*n)),:])
                    t.append(self.time_frame[int(np.floor(i*n))])
                down_sampled = np.asarray(down_sampled)
                t = np.asarray(t)
                return t, down_sampled

    def resample_kin(self, bin_size):
        if self.has_kin == 0:
            print('There is no kinematics in this file.')
            return 0
        else:
            if bin_size < self.bin_width:
                print('Cannot bin kinematics using this bin size')
                return 0
            else:
                down_sampledp = []
                down_sampledv = []
                down_sampleda = []
                t = []
                n = bin_size/self.bin_width
                length = int(np.floor(np.size(self.kin_p, 0)/n))
                for i in range(1, length):
                    down_sampledp.append(self.kin_p[int(np.floor(i*n)),:])
                    down_sampledv.append(self.kin_v[int(np.floor(i*n)),:])
                    down_sampleda.append(self.kin_a[int(np.floor(i*n)),:])
                    t.append(self.time_frame[int(np.floor(i*n))])
                down_sampledp = np.asarray(down_sampledp)
                down_sampledv = np.asarray(down_sampledv)
                down_sampleda = np.asarray(down_sampleda)
                t = np.asarray(t)
                return t, down_sampledp, down_sampledv, down_sampleda




        
    

