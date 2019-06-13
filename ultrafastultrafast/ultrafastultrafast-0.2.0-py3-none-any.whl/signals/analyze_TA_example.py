#Standard python libraries
import copy
import os
import time

#Dependencies
import numpy as np
import warnings
import matplotlib.pyplot as plt
from pyfftw.interfaces.numpy_fft import fft, fftshift, ifft, ifftshift, fftfreq

#UF2
from .plotting_tools import Plotter
from .signal_processing import SignalProcessing

class AnalyzeTransientAbsorption(SignalProcessing,Plotter):

    def __init__(self,parameter_file_path,*,load_file_name='default'):
        self.base_path = parameter_file_path
        self.load(load_file_name=load_file_name)

    def load(self,*,load_file_name='default'):
        if load_file_name == 'default':
            load_name = os.path.join(self.base_path,'TA_spectra_iso_ave.npz')
        else:
            load_name = os.path.join(self.base_path,load_file_name)
        arch = np.load(load_name)
        self.signal = arch['signal']
        self.delay_times = arch['delay_times']
        self.w = arch['frequencies']
        try:
            self.center = arch['pulse_center']
        except KeyError:
            warnings.warn('Pulse center was not saved in archive, setting center = 0')
            self.center = 0
        self.wT = fftshift(fftfreq(self.delay_times.size,d=(self.delay_times[1] - self.delay_times[0])))*2*np.pi

    def get_closest_index_and_value(self,value,array):
        """Given an array and a desired value, finds the closest actual value
            stored in that array, and returns that value, along with its 
            corresponding array index
"""
        index = np.argmin(np.abs(array - value))
        value = array[index]
        return index, value

    def phase_diff(self,signal,w1,w2,wT):
        w1ind, w1 = self.get_closest_index_and_value(w1,self.w)
        w2ind, w2 = self.get_closest_index_and_value(w2,self.w)
        wTind, wT = self.get_closest_index_and_value(wT,self.wT)
        signal_ft = self.ft_axis1(signal)
        return self.phase_diff_by_inds(signal_ft,w1ind,w2ind,wTind)

    def mag_ratio(self,signal,w1,w2,wT):
        w1ind, w1 = self.get_closest_index_and_value(w1,self.w)
        w2ind, w2 = self.get_closest_index_and_value(w2,self.w)
        wTind, wT = self.get_closest_index_and_value(wT,self.wT)
        signal_ft = self.ft_axis1(signal)
        return self.mag_ratio_by_inds(signal_ft,w1ind,w2ind,wTind)

    def integrated_signal(self):
        return np.trapz(self.subtract_DC(self.signal), axis = 0,x = self.w)

    def find_node(self):
        """Finds the location of the vibrational node
"""
        zeros = np.zeros(self.signal.shape[1])
        sig = self.subtract_DC(self.signal)
        for i in range(zeros.size):
            zeros[i] = self.find_zero(self.w,sig[:,i])
        return zeros

    def plot_node(self):
        zeros = self.find_node2()
        plt.plot(self.delay_times,zeros,'--r')
        
    def find_node2(self):
        sig = self.ft_axis1(self.signal)
        wTind, wT = self.get_closest_index_and_value(1,self.wT)
        zero = self.find_zero(self.w,np.imag(sig[:,wTind]))
        return np.ones(self.delay_times.size)*zero
