import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
import tensorflow

# Use Simulation Data

class calTHD():
    def __init__(self,Freq,Amp):
        """
        Define parameters
        if want to use stimulate wave
        """
        # internal parameter
        self.t0=0
        self.tf = 0.02  # integer number of cycles
        self.dt = 1e-4
        self.offset = 0.5
        self.N = int((self.tf-self.t0)/self.dt)
        self.time = np.linspace(0.0,self.tf,self.N )    #;
        
        
        # external parameter
        self.freq = Freq
        self.Amp = Amp
        
        
    def thd(self,myWave):
        """
        Calculate the THD of the target waves
        """
        # Adjust the wave for THD using fast fouriour transformation
        abs_yf = np.abs(np.fft.fft(myWave))
        abs_data=abs_yf[1:int(len(abs_yf)/2) ]
        
        sq_sum=0.0
        
        for r in range( len(abs_data)):
            sq_sum = sq_sum + (abs_data[r])**2

        sq_harmonics = sq_sum -(max(abs_data))**2.0
        thd = 100*sq_harmonics**0.5 / max(abs_data)
        
        #print("The THD for this wave is :")

        return np.round(thd,4)


    def genData(self,waveType):
        
        """
        Simulate some data if needed
        """
        if waveType=="sqr":
            iWave=self.Amp*signal.square(2.0 * np.pi * self.freq * self.time, duty=1/2)+self.offset
        elif waveType=="sine":
            iWave = self.Amp*np.sin(2.0*np.pi*self.freq*self.time) + self.offset
        else:
            print("give correct wave type: sqr or sine")
            
        return iWave
def thdreal(myWave):
    abs_yf = np.abs(np.fft.fft(myWave))
    abs_data=abs_yf[0:int(len(abs_yf)/2)]
    
    sq_peak=[]
    for i in range(1,len(abs_data)-1):
        if abs_data[i]>abs_data[i-1] and abs_data[i]> abs_data[i+1]:
            sq_peak.append(abs_data[i])
    if len(sq_peak)==0:
        sq_peak.append(max(abs_data))
    sq_sum=0.0
    
    for r in range(len(sq_peak)):
        sq_sum = sq_sum + (sq_peak[r])**2

    sq_harmonics = sq_sum -(max(sq_peak))**2.0
    thd = 100*sq_harmonics**0.5 / max(sq_peak)

    #print("The THD for this wave is :")

    return np.round(thd,4)
def plotTHD(fullWave,freq):
    allTHD=[]
    for i in range(len(fullWave)-freq):
        iwave=fullWave[i:i+freq]
        tep=calTHD(100,2).thd(iwave)
        allTHD.append(tep)
    # plot them
    fig=plt.figure(figsize=(16,7))
    fig.suptitle('Compare the THD and the wave shape',color='red')

    plt.subplot(2,1,1)
    plt.title(" Wave Shape")
    plt.plot(fullWave,color='black')

    plt.subplot(2,1,2)
    plt.title("Total Harmonic Distortion",color='blue')
    allTHD0=[0]*freq+allTHD
    plt.ylim(bottom = 0)
    plt.ylim(top = 100)
    plt.plot(allTHD0,color='blue')
def deriveTHD(fullWave,freq):
    allTHD=[]
    for i in range(len(fullWave)-freq):
        iwave=fullWave[i:i+freq]
        tep=calTHD(100,2).thd(iwave)
        allTHD.append(tep)
    allTHD0=[0]*freq+allTHD
    return allTHD0
def fft(myWave):
    abs_yf = np.abs(np.fft.fft(myWave))
    abs_data=abs_yf[1:int(len(abs_yf)/2)]
    return abs_data