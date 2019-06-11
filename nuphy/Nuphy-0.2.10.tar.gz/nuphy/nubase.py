DEBUG=False
import sys
def unitfunc():
    print('i... unitfunc in nubase', file=sys.stderr )
    return True


import sys # stdout.write
import re
import numpy as np
from time import sleep
import os
#
#  accessing data
#
#import os
#this_dir, this_filename = os.path.split(__file__)
#DATA_PATH = os.path.join(this_dir, "data", "data.txt")
###print open(DATA_PATH).read()
import pkg_resources


def isfloat(value):
    ok=False
    try:
        float(value)
        ok=True
    except ValueError:
        return False
    return ok




############ GLOBAL STUFF:  MASSTABLE DATA AND LIST
masstable=''
masslist=[]
massnp=np.zeros( shape=(300,150)  )

massnp=massnp-999999.  # invalid value as initial



elements=['n','H','He','Li','Be','B','C','N','O','F','Ne',
                        'Na','Mg','Al','Si','P','S','Cl','Ar',
                        'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',  'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
                        'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe',
                        'Cs', 'Ba',
                        'La','Ce','Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu','Hf',
                        'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi',
                        'Po', 'At', 'Rn', 'Fr','Ra', 'Ac',  'Th', 'Pa', 'U',
                        'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es',
                        'Fm', 'Md', 'No', 'Lr','Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt',
                        'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']; #110-118

gas=[]   # list 0 or 1 === elements
densities=[0,   0.00008988, 0.0001785,
           0.534,  1.85,  2.34 , 2.267,  0.0012506,   0.001429,  0.001696,  0.0008999, # Ne
           0.971,  1.738, 2.698, 2.3296, 1.82,  2.067,   0.003214, 0.0017837, #Ar
           0.862,  1.54 , 2.989,      4.540,   6.0 ,    7.15 ,   7.21 ,   7.86 ,  8.9,   8.908 ,    8.96,    7.14,
           5.91,  5.32 , 5.72 , 4.79 , 3.12 , 0.003733,
           1.63, 2.54, 4.47, 6.51, 8.57, 10.22, 11.5, 12.37, 12.41, 12.02, 10.5, 8.65,
           7.31, 7.31, 6.68, 6.24, 4.93, 0.005887,
           1.87, 3.59, 6.15,
           6.77, 6.77, 7.01, 7.3, 7.52, 5.24, 7.9, 8.23, 8.55, 8.8, 9.07, 9.32, 6.9, 9.84,
           13.31, 16.65, 19.35, 21.04, 22.6, 22.4, 21.45, 19.32, 13.55,
           11.85, 11.35, 9.75, 9.3,  7.000, 0.00973,   #  ... At, Rn
           1.87, 5.5, 10.07,
           11.72, 15.37, 18.95, 20.45, 19.84, 13.69,   #Th ... Am
           13.51, 14.79, 15.1, 8.84,  #Cm ... Es99
           9.7, 10.3, 9.9, 15.6, 23.2, 29.3, 35.0, 37.1, 40.7, 37.4, # Fm ...Mt109
           34.8, 28.7, 23.7, 16, 14, 13.5, 12.9 , 7.2, 5.0  # Ds110   ... Og118
];
if len(gas)==0:
    for i in densities:
        if i>0.1:
            gas.append(0)
        else:
            gas.append(1)





# molar weight
molarweights=[1,  1.0079, 4.0026,
              6.941, 9.01218, 10.811, 12.0107, 14.0067, 15.9994, 18.998, 20.1797,
              22.98977, 24.305, 26.9815, 28.0855, 30.97376, 32.065, 35.453, 39.948,
              39.0983, 40.078,  44.9559,  47.867,  50.9415, 51.996, 54.938, 55.845,  58.933, 58.693, 63.546,   65.409,
              69.723, 72.64, 74.9216, 78.96, 79.904, 83.8,
              85.4678, 87.62, 88.906, 91.224, 92.9064, 95.94, 98, 101.07, 102.9055, 106.42, 107.8682, 112.411,
              114.818, 118.71, 121.76, 127.6, 126.9045, 131.293,
              132.9055, 137.327, 139.9055,
              140.116, 140.9077, 144.24, 145, 150.36, 151.964, 157.25, 158.925, 162.5, 164.9303, 167.259, 168.9342, 173.04, 174.967,
              178.49, 180.9479, 183.84, 186.207, 190.23, 192.217, 195.078, 196.9665, 200.59,
              204.3833, 207.2, 208.9804, 209, 210, 222,  # At, Rn
              223, 226, 227,                             # Fr, Ra, Ac
              232.0381, 231.0359, 238.0289, 237, 244, 243, #Th .. Pu, Am
              247, 247, 251, 252, 257, 258, 259, 266,267,268,269,270,277, #...Hs108
              278,281,282,285,286,289,290,293,294,294  #  .... Ts117, Og118
];

class isotope:
    '''
    This object has following information:
    Z
    A
    N
    isodensities ...  material density corrected on pure isotope
    mex
    name
    namesrim     .... reverse notation he3 h1 fe56
    amu          .... compare to molarweights
    '''
    massline=''   # MY LINE
    mex=0.0
    dmex=0.0
    spin=0
    halflife=None
    IS=0.0
    name=''
    namesrim=''
    A=0
    Z=0
    N=0
    spin=9999.
    parity=0.0
    amu=0.0
    isodensity=0.0
    def __init__(self, A,  Z=-1,  silent=False):
        '''
        Possibilities of input:
        (4,2)     ... optimal
        (4,'He')  ... if you dont know Z
        NOT ('4He')   ... string
        ('he4')   ... srim like - for srim.py
        '''
        global masstable
        global masslist
        global massnp
        global elements
        ####################################### LOAD MASSTABLE FIRST
        if DEBUG:print("i... ISOTOPE:INIT:  ",A, Z,silent)
        DATA_PATH = pkg_resources.resource_filename('nuphy', 'data/')
        DB_FILE = pkg_resources.resource_filename('nuphy', 'data/nubase2016.txt')
        
        if ( len(masstable)<=0):
            with open(DB_FILE) as f:
                masstable=f.read()
                masslist=masstable.split('\n')
            if DEBUG:print(' D.. masses loaded ... ', len(masslist),'lines')
            for li in masslist:
                if (len(li)>0):
                    #print( li,  int(li[0:3]), int(li[4:7]) ,  )
                    if ( li[7] is '0' ):
                        flo=li[17:24]+'.'+li[25:29]
                        #print(flo, int(li[0:3]), int(li[4:7])  , li)
                        if isfloat( flo ):
                            massnp[ int(li[0:3]), int(li[4:7]) ] = float(  flo )
                    #print( int(li[0:3]), int(li[4:7]),    )
                    #sleep(0.2)
            # i want a map ... numpy [a,z]
######################## MASSTABLE LOADED ######## READ Z A
        if (type(A) is str):         #srimlike
            if DEBUG:print( ' D.. A is str: /'+A+'/  srim like notation' )
            nzmm=re.search(r"([a-zA-Z]+)",   A )
            zname=nzmm.group(1).title()
            #print( A, '.... name is ',nzmm.group(1),'exctracted Z NAME==  ',  zname )
            try:
                #print( elements.index( zname )  )
                self.Z= elements.index( zname )
                #print(self.Z)
            except:
                if not silent: print('!... no such element like', zname, nzmm)
                self.Z=-1
            if self.Z==-1:
                return None
            namm=re.search(r"([\d]+)",   A )
            #print( A, 'exctracted A:  ', namm.group(1) )
            self.A=int( namm.group(1)  )
            #self.A=int( re.sub(r"([\w]+)([\d]+)", r"\2", A ) )
            #print('srim notation: A=',self.A,'Z=',self.Z)
        elif (type(Z) is str):
            if DEBUG:print(" D.. Z is str     classical notation")
            self.A=A
            self.Z=-1
            try:
                self.Z=elements.index(Z)
                ###print(" D.. ", elements)
            except:
                print('X... NO SUCH ELEMENT ',Z)
            if self.Z==-1:
                return None
        else:
            if DEBUG:print(" D.. all numbers notation    A,Z")
            self.A=A
            self.Z=Z
            #print('Z=',Z,' is element',elements[Z])
        if (self.A>=massnp.shape[0]) or (self.Z>=massnp.shape[1]):
            if not silent: print('!... No isotope',A,Z)
            return None
        if A=='n1':
            print("!... overriding automatic A,Z to neuton")
            self.A=1
            self.Z=0
            #self.name='n1'
        A=self.A  # be sure to use int from now
        Z=self.Z
        #########################################
        Anu='%03d' % A
        Znu='%03d0' % Z
        rese='^'+Anu+' '+Znu+' '
        #print( '... going to search ',rese )
        if ( massnp[A,Z]>-999999.):
            for li in masslist:
                if ( re.search( rese , li) ):
                    self.massline=li.rstrip()
                    #print(li)
                    #break
                    if (len(self.massline)>0):
                        self.name=self.massline[10:16].strip()
                        self.namesrim=re.sub(r"([\d]+)([\w]+)", r"\2\1", self.name ).lower()
                        self.mex=massnp[A,Z]
                        self.dmex=   float( self.massline[30:33]+'.'+self.massline[34:38] )
                        halv=self.massline[61:64]+'.'+self.massline[65:68]
                        halv=halv.replace('<', '')
                        halv=halv.replace('>', '')
                        halv=halv.replace('stb.', 'None')  # precisely put 0. for stables
                        #print( halv )
                        if ( isfloat(halv) ):
                            self.halflife=float( halv )
                            #print(  self.halflife )
                        else:
                            self.halflife= None
                            #print(  'NOT FLOAT ',self.halflive )

                        uniti=self.massline[69:71]
                        if (uniti.strip()  == 'Zy'):
                            self.halflife=self.halflife*365*24*3600*1e+24
                        if (uniti.strip()  == 'Zy'):
                            self.halflife=self.halflife*365*24*3600*1e+21
                        if (uniti.strip()  == 'Ey'):
                            self.halflife=self.halflife*365*24*3600*1e+18
                        if (uniti.strip()  == 'Py'):
                            self.halflife=self.halflife*365*24*3600*1e+15
                        if (uniti.strip()  == 'Ty'):
                            self.halflife=self.halflife*365*24*3600*1e+12
                        if (uniti.strip()  == 'Gy'):
                            self.halflife=self.halflife*365*24*3600*1e+9
                        if (uniti.strip()  == 'My'):
                            self.halflife=self.halflife*365*24*3600*1e+6
                        if (uniti.strip()  == 'ky'):
                            self.halflife=self.halflife*365*24*3600*1e+3
                        if (uniti.strip()  == 'y'):
                            self.halflife=self.halflife*365*24*3600
                        if (uniti.strip()  == 'd'):
                            self.halflife=self.halflife*24*3600
                        if (uniti.strip()  == 'h'):
                            self.halflife=self.halflife*3600
                        if (uniti.strip()  == 'm'):
                            self.halflife=self.halflife*60
                        if (uniti.strip()  == 'ms'):
                            self.halflife=self.halflife*1e-3
                        if (uniti.strip()  == 'us'):
                            self.halflife=self.halflife*1e-6
                        if (uniti.strip()  == 'ns'):
                            self.halflife=self.halflife*1e-9
                        if (uniti.strip()  == 'ps'):
                            self.halflife=self.halflife*1e-12
                        if (uniti.strip()  == 'fs'):
                            self.halflife=self.halflife*1e-15
                        if (uniti.strip()  == 'as'):
                            self.halflife=self.halflife*1e-18
                        if (uniti.strip()  == 'zs'):
                            self.halflife=self.halflife*1e-21
                        if (uniti.strip()  == 'ys'):
                            self.halflife=self.halflife*1e-24
                        #print( 'mex %f dmex %f' % (self.mex,  self.dmex ) )

                        IS=self.massline[110:].split(' ')[0]
                        #print("DEBUG...",self.massline)
                        #print("DEBUG...   IS=",IS, "halflife=",self.halflife)
                        if (self.halflife==None):
                            try:
                                self.IS=float( IS[3:])
                            except:
                                self.IS=0.0
                        else:
                            self.IS=0.0
                        self.A=A
                        self.Z=Z
                        self.N=A-Z
                        spin=self.massline[79:93]
                        self.spinfull=spin
                        parity=None
                        if (spin.find('+')>=0):
                            parity=+1
                        if (spin.find('-')>=0):
                            parity=-1
                        spin=spin.replace('+','')
                        spin=spin.replace('-','')

                        spin=spin.replace('(','')
                        spin=spin.replace(')','')
                        spin=spin.replace('#','')
                        if (spin.split() ): spin=spin.split()[0]
                        if (spin.split(',') ): spin=spin.split(',')[0]
                        #spin=spin.split(',')[0]
                        #print( 'SPIN==', spin)
                        spinh=re.findall( r'(\d+)/2', spin)
                        #print("DDD... spinh:", spinh )
                        if ( len(spinh)>0):
                            #print('DDD len>0  spinh:',spinh)
                            spin=int(spinh[0])/2.
                        if (isfloat(spin)):
                            # suddenly - it crashes,spin is str!!
                            #    i patched by i dont believe
                            #
                            ###print("DDD... float of  spin=",spin)
                            self.spin=float( "{:.1f}".format( float(spin) ) )
                        else:
                            self.spin=-9999.
                        self.parity=parity
                        self.amu= (self.mex/1000.  + self.A * 931.49403)/931.49403;
                        #print( self.name , self.mex, self.dmex, self.spin,self.parity, ' ...  ', self.halflife , '?'+uniti.strip()+'?' , IS, self.IS )
                        print("     {:5s} (Z={:3d}) mex={:7.1f} {:s}{:s} amu={:7.4f} g/mol".format(self.name ,self.Z, self.mex, str(self.spin*2)+"/2" if self.spin!=int(self.spin) else str(int(self.spin)),'+' if self.parity==1 else '-', self.amu) , file=sys.stderr)
                        break

        else:
            return None
        self.isodensity=densities[Z]/molarweights[Z]*self.amu
        if not silent:
            print('        rho: elm/iso = {:.3f}/{:.3f} g/cm3 Mm_elm={:6.3f}'.format( densities[Z],self.isodensity,molarweights[Z]) , file=sys.stderr )
            #print('     {}({} {}) rho_iz={:.3f} rho_elm={:.3f} g/cm3 Mm_el={:6.3f} amu={:7.4f} g/mol'.format( self.name,A,Z,self.isodensity,densities[Z],molarweights[Z],self.amu) )
        if len(gas)==0:
            for i in densities:
                if i>0.1:
                    gas.append(0)
                else:
                    gas.append(1)

#########################################################################
###########     ISOTOPE CREATED
#
#
#########################################################################
#        def mex(self):
#                return self.mex
#        def dmex(self):
#                return self.dmex
#        def halflife(self):
#                return self.halflife
#        def IS(self):
#                return self.IS
#        def name(self):
#                return self.name




###########################
#             MAIN
####################################################################
if __name__ == "__main__":
    print("i... ReadNuBase.py is being run directly...")
    print("i... n14:")
    n14=isotope( 14,'N' )
    print("i... n15:")
    n15=isotope( 15,7 )
    print("i... o15:")
    o15=isotope( 15,8 )
    print("----------------------------------- AMU:")
    print("I... AMU", n14.name,n14.amu )
    print("I... AMU", n15.name,n15.amu )
#    print( 'n14 half, spin, parity', n14.halflife , n14.spin , n14.parity , n14.IS )
#    print( 'n15 half, spin, parity', n15.halflife , n15.spin , n15.parity , n15.IS )
    print( 'i... o15 halfl/spin/parity/mex/abund', o15.halflife , o15.spin , o15.parity , o15.mex, o15.IS)
#for a in range(260):
#        for z in range(200):
#                he3=isotope(a,z)
        ###print( he3.mex   )
        ###print( he3.mex, he3.dmex, he3.halflife )
        ###if (he3.name):print( he3.name, he3.mex, he3.dmex, he3.halflife, he3.IS , he3.A, he3.Z, he3.N , he3.spinfull, he3.spin, '*')
#                if (he3.name):print( he3.name, he3.spinfull, he3.spin, he3.parity, '*')
        ###print( he3.mex, he3.dmex, he3.halflife, he3.IS()  )
    print("----------------------------------------------- end")
#else:
#    print("")
    #print("ReadNubase is being imported into another module")






    

print("i... module  nubase  is being loaded", file=sys.stderr)
if __name__=="__main__":
    print("i... in nubase ")
