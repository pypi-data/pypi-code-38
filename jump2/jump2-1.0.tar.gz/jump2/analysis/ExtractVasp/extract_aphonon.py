# coding: utf-8
# Copyright (c) JUMP2 Development Team.
# Distributed under the terms of the JLU License.


#=================================================================
# This file is part of JUMP2.
#
# Copyright (C) 2017 Jilin University
#
#  Jump2 is a platform for high throughput calculation. It aims to 
#  make simple to organize and run large numbers of tasks on the 
#  superclusters and post-process the calculated results.
#  
#  Jump2 is a useful packages integrated the interfaces for ab initio 
#  programs, such as, VASP, Guassian, QE, Abinit and 
#  comprehensive workflows for automatically calculating by using 
#  simple parameters. Lots of methods to organize the structures 
#  for high throughput calculation are provided, such as alloy,
#  heterostructures, etc.The large number of data are appended in
#  the MySQL databases for further analysis by using machine 
#  learning.
#
#  Jump2 is free software. You can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published 
#  by the Free sofware Foundation, either version 3 of the License,
#  or (at your option) and later version.
# 
#  You should have recieved a copy of the GNU General Pulbic Lincense
#  along with Jump2. If not, see <https://www.gnu.org/licenses/>.
#=================================================================

"""
Module for extract data from vasp output: phonon spectra. 
"""

class TempPhonon(object):

    """
    To get the frequencies from the phonon with considering the
    amharmonic effects.

    funtionals:
        get_frequencies: get data from FREQ files;
        sparse_frequencies: sparse frequencies to eliminate the 
        numerical error;

    """
    def __init__(self):
        
        pass
    def get_frequencies(self, name):

       data = {}
       xaix = []
       data['energy'] = []
       data['freqen'] = []
       f = open(name,'r')
       while True:
           line = f.readline()
           if not line:
               break
           else:
               tmp = line.split()
               data['energy'].append(float(tmp[0]))
               data['freqen'].append(tmp[1:])
       freq = []
       eneg = data['energy']
       for j in xrange(len(data['freqen'][0])): 
           tmp = []
           for i in xrange(len(data['freqen'])):
                tmp.append(float(data['freqen'][i][j]))
           freq.append(tmp)     
       data = None
      
       return eneg, freq

    def sparse_frequencies(self):
        freq = []
        energy = []
        for i in xrange(1,11):
            data =[]
            f = open('FREQ{0}'.format(i),'r')
            while True:
                line = f.readline()
                if not line:
                   break
                else:
                   tmp = []
                   if i == 1: energy.append(float(line.split()[0]))
                   tmp = line.split()[1:-1] 
                data.append(tmp)
            f.close()
            for j in xrange(len(data[0])):
                tmp = []
                for i in xrange(len(data)):
                    tmp.append(float(data[i][j]))
                freq.append(tmp)
       
        return energy, freq           
       
    def plot_frequencies(self):
        
        pass
#   from matplotlib import pyplot as plt 
#   energy, frequency = spltfreq()
#   fig = plt.figure()
#   for i in xrange(len(frequency)):
#       plt.plot(energy, frequency[i],'r-')
#   plt.xlim(min(energy),max(energy))
#   plt.axhline(linestyle='--',color='k')
#   plt.xticks([energy[0],energy[99],energy[199],energy[299],energy[399]],
#   ['$\mathregular{X}$','$\mathregular{\Gamma}$','$\mathregular{W}$',
#   '$\mathregular{\Gamma}$','$\mathregular{L}$'],fontsize=12)
#   plt.ylim(-0.5,6.5)
#   plt.ylabel('Frequencies (THz)',fontsize=14)
#   plt.savefig('Cs2InSBCl6_phon.png',dpi=400)
#plt.show()
#for i in range(1,22):
#    energy, frequency = data('FREQ.{0}'.format(str(i)))
#    
#    fig = plt.figure()
#    
#    
#    for i in xrange(len(frequency)):
#    
#        plt.plot(energy, frequency[i],'r-') 
#    
#    
#    plt.show()
