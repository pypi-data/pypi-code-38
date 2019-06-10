#!/usr/bin/env python 

import os 


class GetBand(object):
    
    """
    To extract the needed information for plotting the organized the band 
    strucutures from splitted folders.

    functionals:
        get_EignValue: get all the eigenvalues;
        get_ValidK: get the focused kpoints;
        distance2kpt: get the delta distance between two nearest kpoints;

    """

    @property
     def vbm(self):
	"""
        return dict('x':float, 'y':float)
        """
        pass 
    
    @property
     def cbm(self):
	"""
        return dict('x':float, 'y':float)
        """
        pass
    
    @property
     def ispin(self):
	"""
        return 1 or 2
        """
        pass
    
    @property
    def nelect(self):
	"""
        return a integer
        """
        pass
    
    @property
    def symbols(self):
	"""
        return dict('x':float, 'y':float)
        """
        pass
    
    @property
    def eigenvalue(self):
	"""
        return a list
        """
        pass
    
    @property
    def kpoints(self):
	"""
        return a list
        """
        pass
   
    @property
    def gap(self):
	"""
        return dict('direct':
                            dict('coord':(P1,P2), 'value':float), 
                   'indirect':
                            dict('coord':(P1,P2), 'value':float))
        """
        pass
    
    @property
    def projected_bands(self):
        pass
          
        vbm = self.bands.vbm
        cbm = self.bands.cbm
        ispin = self.bands.ispin
        nelect = self.bands.nelect

        symbols = self.bands.symbols # symbols of high symmetrized points % 
        eigenvalues = self.bands.eigenvalue # eigenvalues of all the bands %
        kpoints = self.bands.kpoints # kponts along high symmetrized pathway % 
        direct_gap = self.bands.gap['direct'] # direct gap value % 
        indirect_gap = self.bands.gap['indirect'] # indirect gap value % 
        proband = self.bands.projected_bands # projected bands % 

    
    def __init__(self,path=None, **kwargs):
        
        if path is None: path = os.getcwd()
	self.path = path
    def get_EignValue(self):

	nkpoints = 0
        nbands   = 0
        efermi   = 0.0
        isband   = False
	data     = {}
        try: 
            f = open(self.path+'/OUTCAR','r')
        except IOError:
            print "No OUTCAR" 
	    f.close()

	lines = f.readlines()
	f.close()
	for line in lines:
	    if 'NBANDS=' in line: 
                nkpoint = int(line.split()[3])
                nbands  = int(line.split()[-1])
            if 'E-fermi' in line:
		efermi  = float(line.split()[2])
	f = open(self.path+'/OUTCAR','r')
	while True:	
	    line = f.readline()
	    if not line:
	        break
	    else:
		if 'E-fermi' in line:
		    line = f.readline()
		    line = f.readline()
		    for i in xrange(0,nkpoint):
		        line = f.readline()
			tmp = []
			nk  = int(line.split()[1])
			data[nk] = {}
			for i in xrange(0,3): tmp.append(float(line.split()[-3+i]))
			data[nk]['kpt'] = tmp
		        line = f.readline()
                        tmp1 = {}
			for j in xrange(0,nbands):
			   line = f.readline()
			   if len(line.split()) == 3:
			       tmp1[line.split()[0]] = {}
			       tmp1[line.split()[0]]['energy'] = float(line.split()[1]) - efermi 
			       tmp1[line.split()[0]]['occupd'] = float(line.split()[2]) 
			line = f.readline()
			data[nk]['band']  = tmp1 
	f.close()
	return data
	
    def get_ValidK(self):
    
        f =open(self.path+'/KPOINTS')
        line = f.readline()
        line = f.readline()
        line = f.readline()
        
        n = 0 
        while True:
     	   line = f.readline()
     	   if not line:
     	       break
     	   else:
               if line == '\n': continue 
     	       if float(line.split()[3]) != 0.0:
     	   	    n += 1
        f.close()

        return n

    def modfBand(self):
        
        band = self.getEignValue()
        invl = self.getValidK()
        for i in xrange(1,invl+1):
    	    band.pop(i)
        return band

    def distance2kpt(self, x,y):
        import math 

        delta = 0.0
        sum   = 0.0 
        for i in range(0,3):
            
            sum += math.pow((x[i]-y[i]),2)
        
        return math.sqrt(sum)
    
    def plot_bandstructure(self):

        pass 
#   data = {}
#   n = 0

#   #itertems all the jobfolder contained the scf calculation data. 
#   for i in xrange(1,6):
#       p='scf'+str(i) 
#       a=SplitBand(path=p)
#       bandtmp = a.modfBand() 
#       keytmp = sorted(bandtmp.keys())
#       for j in keytmp:
#           data[n] = bandtmp[j]
#           n += 1
#       

#   banddata= {}
#   kpoints = []
#   kpttmp = sorted(data.keys())

#   for i in kpttmp:
#       bdtmp = sorted(data[i]['band'].keys())
#       n = 0
#       kpoints.append(data[i]['kpt'])
#       for j in bdtmp:
#          if banddata.has_key(n):
#              banddata[n].append(data[i]['band'][j]['energy'])
#          else:
#              banddata[n] = []
#              banddata[n].append(data[i]['band'][j]['energy'])
#          n += 1
#   distance = [0.0]
#   for i in xrange(0,len(kpoints)-1):
#       distance.append(distance[-1]+distance2kpt(kpoints[i],kpoints[i+1]))

#   from matplotlib import pyplot as plt 

#   fig = plt.figure()

#   bdktmp = sorted(banddata.keys())

#   for i in bdktmp:
#       plt.plot(distance,banddata[i],'k-',linewidth=2.0)
#   plt.xlim(0,3.0)
#   plt.ylim(-4,4)
#   plt.show()





