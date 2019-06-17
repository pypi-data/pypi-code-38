#Standard python libraries
import os

#Dependencies
import numpy as np
import yaml
import matplotlib.pyplot as plt
from pyfftw.interfaces.numpy_fft import fft, fftshift, ifft, ifftshift, fftfreq
from scipy.optimize import brentq as sbrentq
from scipy.interpolate import interp1d as sinterp1d

class SignalProcessing(object):
    def subtract_DC(self,signal,return_ft = False, axis = 1):
        """Use discrete fourier transform to remove the DC component of a 
            signal.
        Args:
            signal (np.ndarray): real signal to be processed
            return_ft (bool): if True, return the Fourier transform of the 
                              input signal
            axis (int): axis along which the fourier trnasform is to be taken
"""
        sig_fft = fft(signal,axis=axis)
        sig_fft[:,0] = 0
        if not return_ft:
            sig = np.real(ifft(sig_fft))
        else:
            sig = sig_fft
        return sig

    def integrate(self,x,signal,*,axis = 0):
        return np.trapz(signal,x=x,axis=axis)

    def ft_axis1(self,signal,zero_DC=True):
        # sig_ft = fft(ifftshift(signal,axes=(1)),axis=1)
        sig_ft = fft(signal,axis=1)
        if zero_DC:
            sig_ft[:,0] = 0
        return fftshift(sig_ft,axes=(1))

    def phase_2d(self,signal,ind0,ind1):
        val = signal[ind0,ind1]
        phase = np.arctan2(np.real(val),np.imag(val))
        return phase

    def phase_diff_by_inds(self,signal,w1_ind,w2_ind,wT_ind):
        ph1 = self.phase_2d(signal,w1_ind,wT_ind)
        ph2 = self.phase_2d(signal,w2_ind,wT_ind)
        diff = ((ph1-ph2 + np.pi) % (2*np.pi) - np.pi)
        return diff

    def mag_ratio_by_inds(self,signal,w1_ind,w2_ind,wT_ind):
        mag1 = np.abs(signal[w1_ind,wT_ind])
        mag2 = np.abs(signal[w2_ind,wT_ind])
        return mag1/mag2

    def integrated_ft(self,delay_time_start = 1,delay_time_stop = 300):
        delay_time_indices = np.where((self.delay_times > delay_time_start) & (self.delay_times < delay_time_stop))[0]
        delay_times = self.delay_times[delay_time_indices]
        sig = self.signal_vs_delay_times[:,delay_time_indices]
        integrated = np.trapz(sig,x=self.TA.w,axis=0)
        w_T = fftshift(fftfreq(delay_times.size,d=(delay_times[1] - delay_times[0])))*2*np.pi
        integrated_fft = fft(integrated)
        integrated_fft[0] = 0
        integrated_fft = fftshift(integrated_fft)
        return w_T, integrated_ft
        
    def find_zero(self,x,arr):
        """Given an input 1d array, extrapolate a zero crossing
"""
        y = sinterp1d(x,arr)
        try:
            zero = sbrentq(y,-1,1)
        except:
            print(y(-1),y(1))
            zero = np.nan
        return zero
