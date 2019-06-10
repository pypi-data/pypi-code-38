#!/usr/bin/env python 
import os,sys,math
from pymatgen.io import vaspio

class Pband(object):

   def __init__(self,shift=0.0,correct=False):

       self.__dos  = self.__orbital_pdos()
       self.eigenval = self.__eigenval(shift=shift,correct=correct) 
       self.symbol = self.__symbols()
       self.elements = self.__elements()
 
   def plot_bandstructure(self):

       pass
  
   def pdos(self,band=None,points=None,elments=None,orbitals='s',path='PROCAR'):

       projdos = self.__dos
       atoms = []
       for elm in self.elements:
           if elm in elments:
               atoms.append(1)
           else:
               atoms.append(0)

       if orbitals== 's':
           i = 0;e = 1
       if orbitals== 'p':
           i = 1; e = 4
       if orbitals== 'd':
           i = 4; e = 9
       ei = 3; ee = 4
       projband = {} 
       for b in band:
           projband[b] = []
           for k in xrange(0,len(projdos)):
               tmpdos = 0.0
               for a in xrange(len(atoms)):
                   if atoms[a] == 1: tmpdos += sum(projdos[k][b-1][a][i:e])
               projband[b].append(tmpdos)
       return projband 

   def __orbital_pdos(self,path='PROCAR'):
            
       f = open(path,'r')
       projdos = {}
       tmp = f.readline()
       kbi = f.readline().strip().strip('#').split('#')
       num_k = int(kbi[0].split(':')[-1])
       num_b = int(kbi[1].split(':')[-1])
       num_i = int(kbi[2].split(':')[-1])
       k = 0
       nextk = False
       while (k <= num_k):
           line = f.readline()
           if not line:
               break
           elif len(line.split()) == 0:
               continue 
           elif 'point'  in line or nextk:
               nextk = False
               b = 0
               projdos[k] = {}
               while (b <= num_b):
                   line = f.readline()
                   if not line:
                       break 
                   if 'point' in line:
                       nextk = True 
                       break 
                   if 'band' in line:
                       projdos[k][b] = {}
                       line = f.readline()
                       line = f.readline()
                       for j in xrange(num_i):
                           projdos[k][b][j] = []
                           line = f.readline()
                           for i in line.split()[1:-1]:
                               projdos[k][b][j].append(float(i))
                       b += 1
                   else:
                       continue
               k += 1
       f.close()
       return projdos 
       
  
   def __eigenval(self,path='OUTCAR',shift=0.0,correct=False):
       
       nbands = 0
       nkpts  = 0
       efermi = 0
  
       ckpoints = []
       kdistance = []
   
       # Read the number of fermi level, kpoints and bands.
       tmp0   = os.popen("grep 'NBANDS='  {0}".format(path)).readline().split()
       nkpts  = int(tmp0[3])
       nbands = int(tmp0[14])

       efermi = os.popen("grep 'E-fermi'  {0}".format(path)).readline().split()[2]
      
       # Grep data from OUTCAR.
       cmd1 = "grep 'k-point' {0}>  tmp1.data".format(path)
       cmd2 = "tail -{0} tmp1.data > kpoints.data".format(str(nkpts))
       cmd3 = "grep -A{0} 'band No.  band energies     occupation' \
                   {1} > tmp3.data".format(str(nbands),path)

       cmd4 = "sed  '/--/d' tmp3.data > engery.data"
       cmd5 = "rm tmp?.data kpoints.data engery.data"

       os.system(cmd1), os.system(cmd2), os.system(cmd3),os.system(cmd4)
   
       #Get the distance between ajacent kpoints.
       f = open('kpoints.data')
       for i in xrange(nkpts):
            ckpoints.append((f.readline().split()[3:]))
       f.close()
   
       ### calculate distance between two neighbor kpoints ###
       kdistance = []        # increasing distance with kpoints
       distance  = 0
   
       kdistance.append(0)
       for i in xrange(1, nkpts):
            dx    = float(ckpoints[i][0])-float(ckpoints[i-1][0])
            dy    = float(ckpoints[i][1])-float(ckpoints[i-1][1])
            dz    = float(ckpoints[i][2])-float(ckpoints[i-1][2])
            delta = math.sqrt(math.pow(dx,2)+math.pow(dy,2)+math.pow(dz,2))
            distance += delta
            kdistance.append(distance)
   
       #Get the band energy level.
       eigval = [ [0.0 for kk in xrange(nkpts)] for bb in xrange(nbands) ]
       maxer = -100.0
       miner =  100
       vbmkp =  0
       cbmkp =  0
       vbmkk =  0
       erbar =  0.0
   
       f = open('engery.data')
       for kk in xrange(nkpts):
            f.readline()
            for bb in xrange(nbands):
                 tmp = 0.0
                 tmp = float(f.readline().split()[1])-float(efermi)
                 #tmp = float(f.readline().split()[1])
                 eigval[bb][kk] = tmp
   
                 if tmp <= 0 and tmp >= maxer:
                     maxer = tmp
                     vbmkp = kk
                     vbmkk = bb
                 if tmp >= 0 and tmp <= miner:
                     miner = tmp
                     cbmkp = kk
       f.close()
      ## correct the fermi level.
       erbar = 0.0 - maxer
       for kk in xrange(nkpts):
            for bb in xrange(nbands):
                 eigval[bb][kk]=eigval[bb][kk]+erbar
                 if shift != 0.0 and correct:
                     if eigval[bb][kk] >  0.0: 
                         eigval[bb][kk]=eigval[bb][kk]+shift
                 if shift != 0.0 and not correct:
                     if eigval[bb][kk] >= 0.0: 
                         eigval[bb][kk]=eigval[bb][kk]+shift
      ## remove the tmp files 
       os.system(cmd5)

       self.kpoints = kdistance
       
       return eigval 

   def __elements(self,path='POSCAR'):
 
       from ase.io import vasp
 
       f = vasp.read_vasp(path)

       return f.get_chemical_symbols()
      

   def __symbols(self,path='KPOINTS'):

       '''Get the high symmetric paths'''
       
       kpoints = vaspio.Kpoints.from_file(path)
        
       return kpoints.labels 


   def save_data(self,name='bandstr.data',*kwargs):
       
       import cPickle as pickle 

       pickle.dump((kwargs),(open(name,'wb')))  

       
