#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import os,sys
import math
from matplotlib.font_manager import FontProperties


__contributor__ = 'Xingang Zhao'

try:
    from ase.io import read 
except:
    raise ImportError("No ASE module")

class extractPDOS(object):

    """
    Get the projected density of states from DOSCAR.
    CONTCAR/DOSCAR files are needed.

    
    """
    def __init__(self, path=None, *args, **kwargs):
	
        if path is None: 
	    path = os.getcwd()
	self.ispin = 1
	self.dos = None 
	self.path = path
	if os.path.exists(path+'/CONTCAR'):
	    self.structure = read(path+'/CONTCAR')
	else:
	    raise IOError ('No CONTCAR.')
    
    # get lattice vector from structure % 
    def __get_lattice(self):
	a, b, c = self.structure.get_cell_lengths_and_angles()[0:3]	
	volume = self.structure.get_volume()
        return a, b, c, volume

    # get element information from CONTCAR
    def __getElementinfo(self):
	from collections import Counter
	symbols = self.structure.get_chemical_symbols()
	elements = list(set(symbols))
	elements.sort(key=symbols.index)
	elm = Counter(symbols)

        elementNumbers = []
	for k in elements: 	
 	    elementNumbers.append(elm[k])	
	
        totalAtomNumbers = len(symbols)
	del elm 
        return elements, elementNumbers, totalAtomNumbers
    
    def __get_orbitals(self):
	
	lorbit = 0
	ispin = 1
        with_soc = False 
        orbital = {}
	path = self.path+'/OUTCAR'
	if os.path.exists(path):
	    temp = os.popen('grep LORBIT {0}'.format(path)).readline()
            lorbit = int(temp.split()[2])
	    temp = os.popen('grep ISPIN {0}'.format(path)).readline()
            ispin = int(temp.split()[2])
	    temp = os.popen('grep LNONCOLLINEAR {0}'.format(path)).readline()
            if str(temp.split()[2]) == 'T':
		with_soc = True
                ispin = 1
	    temp = os.popen('grep VRHFIN {0}'.format(path)).readlines()
            string = []
	    for l in temp: string.append(l.split(':')[-1].strip())
	    orbitals = ''.join(string)
            for o in ['s', 'p', 'd', 'f']:
		if o in orbitals: orbital[o] = []	    
	else:
	    raise IOError ("No OUTCAR.")
	del temp, orbitals 

	# get index with respect to orbital % 	
	if lorbit != 0:
	    if with_soc is True:
	        for o in orbital:
		    if o == 's' and lorbit == 10:
		        orbital[o] = [1]	    
		    if o == 's' and lorbit > 10:
		        orbital[o] = [1]	    
		    if o == 'p' and lorbit == 10:
		        orbital[o] = [5]	    
		    if o == 'p' and lorbit > 10:
		        orbital[o] = [5, 9, 13]	    
		    if o == 'd' and lorbit == 10:
		        orbital[o] = [9]	    
		    if o == 'd' and lorbit > 10:
		        orbital[o] = [17, 21, 25, 29, 33]	    
		    if o == 'f' and lorbit == 10:
		        orbital[o] = [13]	    
		    if o == 'f' and lorbit > 10:
		        orbital[o] = [37,41,45,49,53,57,61,65,69,73,77,81,85,89]
	    else:
	        for o in orbital:
		    if o == 's' and lorbit == 10:
		        orbital[o] = [1]	    
		    if o == 's' and lorbit > 10:
		        orbital[o] = [1]	    
		    if o == 'p' and lorbit == 10:
		        orbital[o] = [2]	    
		    if o == 'p' and lorbit > 10:
		        orbital[o] = [2, 3, 4]	    
		    if o == 'd' and lorbit == 10:
		        orbital[o] = [3]	    
		    if o == 'd' and lorbit > 10:
		        orbital[o] = [5, 6, 7, 8, 9]	    
		    if o == 'f' and lorbit == 10:
		        orbital[o] = [4]	    
		    if o == 'f' and lorbit > 10:
		        orbital[o] = [10,11,12,13,14,15,16,17,18,19,20,21,22,23]
	
	return ispin, orbital		 		    
	
    @staticmethod 
    def __get_pdos(line, orbital):
	# s/p/d orbital % 
	v = 0
	for o in orbital:
	    v += line[o]
	del line, orbital
	return v 	
 
    # get dos from DOSCAR
    def get_DOS(self, *args, **kwargs):

	dos = {'total':{'up':[],'down':[]}, \
		'pdos':{'up':[],'down':[]}, \
	        'nume':{'up':[],'down':[]}}	

        ispin = 1
	energy = []
        elm, numelm, numatom = self.__getElementinfo()
	ispin, orbital = self.__get_orbitals()
		
	with open(self.path+'/DOSCAR') as f:

            # skip comment lines
            for i in range(0,5): string = f.readline()
            
            string = f.readline()
            points = int(string.split()[2])
            efermi = float(string.split()[3])
           
            # read total DOS
            for i in range(0, points):

                string = f.readline()
                temp = [float(s0) for s0 in string.split()]
		energy.append(temp[0])

		if ispin == 1:
		    dos['total']['up'].append(temp[1])
		    dos['nume']['up'].append(temp[2])
		if ispin == 2:
		    dos['total']['up'].append(temp[1])
		    dos['total']['down'].append(temp[2])
		    dos['nume']['up'].append(temp[3])
		    dos['nume']['down'].append(temp[4])
           
	    order_orbital = ['s','p', 'd', 'f']
	    orbitals = orbital.keys()
	    orbitals.sort(key=order_orbital.index)
            
	    for i in range(0, numatom):
                isf = f.readline() # skip % 
           	if not isf: break  # no pdos % 
                print "read:" , i+1, "atoms"
		temp_dos_up = []
		temp_dos_down = []
                for j in range(0, points):
                    up = []
                    down = []
                    string = f.readline()
                    temp = [float(s0) for s0 in string.split()]
		    for o in orbitals:
			o_index = np.array(orbital[o])
			up.append(self.__get_pdos(temp, o_index))
		    temp_dos_up.append(up)
 			
            	    if ispin == 2:
		        for o in orbitals: 
			    o_index = np.array(orbital[o])
			    down.append(self.__get_pdos(temp, o_index+1))
			temp_dos_down.append(down)

                dos['pdos']['up'].append(np.array(temp_dos_up))
                dos['pdos']['down'].append(np.array(temp_dos_down))
	 	del temp_dos_up
		del temp_dos_down
       # pdos of element
      #elementPDOS = [0]*len(elementNumbers)
        counter = 0
        dos['element'] = {}
        for i in elm:
            dos['element'][i] = {}
            up = None
            down = None
            for j in range(0, numelm[elm.index(i)]):
		if up is None: up = dos['pdos']['up'][counter]
		if down is None: down = dos['pdos']['down'][counter]
                up += dos['pdos']['up'][counter] 
                if ispin == 2: 
                    down += dos['pdos']['down'][counter] 
                counter += 1
            dos['element'][i]['up'] = up.T
            dos['element'][i]['down'] = down.T
            del up, down

	return np.array(energy) - efermi,ispin, dos 

    # plot element pdos
    def plotPDOS(self, ax, linstyle=None, average='volume', colors=None,show=True):

	"""
	Projected Density of States averaged by lattice Volume. 
	"""	
	plt = ax  
	# basic set % 
        linestyle = [":", "--", "-", "-."]
        colors = ["r", "g", "b", "c", "m", "orangered"]
        obrt=['s','p','d', 'f']

        energy, ispin, dos = self.get_DOS()
        a, b, c, volume = self.__get_lattice()
        if ispin == 1:
	    plt.plot(energy, dos['total']['up']/volume, "-", color="k",linewidth=2.0, label="total")
	if ispin == 2:
	    plt.plot(energy, dos['total']['up']/volume, "-", color="k",linewidth=2.0, label="total")
	    plt.plot(energy, np.array(dos['total']['down'])*-1.0/volume, "-", color="k",linewidth=2.0)
        plt.axvline(x=0, linestyle="--", color="r")
        # I
        if ispin ==2:
            n = 0
            for j in dos['element']:
        	for i in range(0,len(dos['element'][j]['up'])):
        	      plt.plot(energy, dos['element'][j]['up'][i]/volume, \
		      linestyle[n],linewidth=2.0, color=colors[i], label=j+"-"+obrt[i])
                n += 1
            n = 0 
            for j in dos['element']:
        	for i in range(0,len(dos['element'][j]['down'])):
        	      plt.plot(energy, dos['element'][j]['down'][i]*-1.0/volume, \
		      linestyle[n],linewidth=2.0, color=colors[i])
                n += 1
        else:
            n = 0 
            for j in dos['element']:
        	for i in range(0,len(dos['element'][j]['up'])):
        	      plt.plot(energy, dos['element'][j]['up'][i]/volume,\
		      linestyle[n],linewidth=2.0, color=colors[i], label=j+"-"+obrt[i])
                n += 1

	plt.xlabel("$\mathregular{Energy\ (eV)}$", fontsize=16).set_fontweight("bold")
	plt.ylabel(r"$\mathregular{PDOS\ (states/eV/\AA^{3})}$", fontsize=16).set_fontweight("bold")
	plt.xlim(-5,5)
	plt.xticks(fontsize=18)
	plt.yticks(fontsize=18)
	plt.tick_params(labelsize=14)
	plt.legend(loc=2, prop=(FontProperties(weight="bold", size=12)), ncol=4, frameon=False)
	plt.tight_layout()
	if show is True : plt.show()

# main % ################################################
p = AbstractPDOS()
fig = plt.figure(figsize=(8,8))
p.plotPDOS(plt)
#plt.savefig("DOS.png", dpi=300)
