#!/usr/bin/python3

import sys
#sys.path.insert(0, '.') #  I PUT PRIORITY TO LOCAL DEVELOPMENT

import os

#import srim  
import nuphy.srim  as srim
import nuphy.nubase as nubase


import subprocess
from distutils.dir_util import copy_tree  # copytree
import tempfile   # create tempdir
from contextlib import contextmanager       # for CD with context


################################
# i need interpolation now.... #
#https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np


import scipy.integrate as integrate

from xvfbwrapper import Xvfb  # invisible RUN :  remote run NEEDS THIS




OUTPUTFILE="output"

#
# stopping units  eV/ ( 1E15 atoms/cm2 )   : 7
#

MANUAL_SR_IN="""---Stopping/Range Input Data (Number-format: Period = Decimal Point)
---Output File Name
"OOOUTPUTFILE"
---Ion(Z), Ion Mass(u)
1   1.008
---Target Data: (Solid=0,Gas=1), Density(g/cm3), Compound Corr.
0    1.0597    .9457121
---Number of Target Elements
 3 
---Target Elements: (Z), Target name, Stoich, Target Mass(u)
1   "Hydrogen"               8             1.008
6   "Carbon"                 3             12.011
8   "Oxygen"                 2             15.999
---Output Stopping Units (1-8)
 7
---Ion Energy : E-Min(keV), E-Max(keV)
 10    10000
""";


MANUAL_SR_IN="""---Stopping/Range Input Data (Number-format: Period = Decimal Point)
---Output File Name
"OOOUTPUTFILE"
---Ion(Z), Ion Mass(u)
1   1.008
---Target Data: (Solid=0,Gas=1), Density(g/cm3), Compound Corr.
0    2.253    1
---Number of Target Elements
 1 
---Target Elements: (Z), Target name, Stoich, Target Mass(u)
6   "Carbon"                 1             12.011
---Output Stopping Units (1-8)
 7
---Ion Energy : E-Min(keV), E-Max(keV)
 10    10000
""";

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    dirname=os.path.dirname( newdir )

    os.chdir(os.path.expanduser( dirname ))
    #print('i... from',prevdir,'entering',dirname )
    try:
        yield
    finally:
        #print('i... cd back to ',prevdir)
        os.chdir(prevdir)



        

def load_SR_file( SRFile ):
    """
    reads the file 
    returns DICT with losses at certain energies
    """
    units_ok=False
    kevum=0.0
    mevmg=0.0  # MeV/mg/cm2
    with open( SRFile ) as f:
        li=f.readlines()

    li=[x.rstrip() for x in li] # remove \n
    begin,end=0,len(li)
    for i in range(len(li)):
        if (li[i].find("Energy")>=0) and  (li[i].find("Nuclear")>=0):
            begin=i+2
        if  (li[i].find("Multiply")>=0) and  (li[i].find("Stopping")>=0):
            end=i-1
        if  (li[i].find("eV/(1E15 atoms/cm2)")>=0) and  (li[i].find("1.0000E+00")>=0):
            units_ok=True
        if  (li[i].find("keV/micron")>=0):
            kevum=float( li[i].strip().split()[0] )
            print( ".... kevum=",kevum)
        if  (li[i].find("MeV/(mg/cm2)")>=0):
            mevmg=float( li[i].strip().split()[0] )
            print( ".... mevmg=",mevmg)
    if not units_ok:
        print("X... I am afraid the unit is not 7 / eV/(1E15 atoms/cm2).QUIT")
        quit()
    li=li[begin:end]
    #print(  li  )
    eneloss={}
    factor=1 ######000000  # eV => MeV
    for i in li:
        a=i.strip().split()
        ene=float(a[0])
        loss=float(a[2]) + float(a[3])
        #print(".... .... ", loss,float(a[2]) , float(a[3]) )
        #all in eV
        if a[1]=="keV":
            #ene=ene*1000.
            ene=ene/1000.
        if a[1]=="MeV":
            #ene=ene*1000000.
            ene=ene
        # change units for some reason
        eneloss[ ene ] =loss /factor # eV  => MeV/ (10^15/cm2)
    ###kevum=kevum*factor
    return eneloss,kevum,mevmg






def run_sr_exe( SRINFILE=MANUAL_SR_IN,  silent=True):
    """
    returns DICT  eneloss
    """
    RPATH=srim.CheckSrimFiles()
    if not silent:print( "DDD...    SR.IN:",RPATH ," xxx")
    
    ############## CREATE TEMP #####################
    temppath = tempfile.mkdtemp(prefix='sr_')+'/'
    if not silent: print('DDD... SR.IN ... copying from',RPATH,'to',temppath)
    copy_tree( RPATH , temppath )
    #print("DDD...  copied")
    with cd(temppath+'SR Module/'):
        if not silent:print("DDD... cd "+temppath+'SR\\ Module/')
        #srin=MANUAL_SR_IN.replace("OOOUTPUTFILE", OUTPUTFILE)+"\n"
        srin=SRINFILE.replace("OOOUTPUTFILE", OUTPUTFILE)+"\n"
        if srin.find("\r\n")<0:
            srin=srin.replace('\n','\r\n') # DOS 
        with open("SR.IN","w") as f:
            f.write(srin)
        CMD="wine SRModule.exe"
        if not silent:print("DDD... ",CMD)
        if silent:
            print("############### VDISPLAY #########################start")
            vdisplay = Xvfb(width=1280, height=740, colordepth=16)
            vdisplay.start()
            
        process = subprocess.Popen(CMD.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)            
        output, error = process.communicate()
         
        if silent:
            vdisplay.stop() #
            #print()
            print("\n############### VDISPLAY #########################stop")
            
        if not silent:print("DDD...  reading losses of SR.IN from ouput")
        eneloss,kevum,mevmg=load_SR_file( OUTPUTFILE )
        #print("losses and keV/um coef read")
    #print( "output==",eneloss )
    return eneloss,kevum,mevmg  # DICT WITH LOSSES





def srinterpolate( eneloss , plot=False):
    """
    get DICT of losses, create numpy arrays with interpolations
    return spline function
    that can be used like

    resu=interpolate.splev(x, splinefunction , der=0)
    print( "dE/dx value at 1.0MeV" , get_tcks(1.0)  )

    """
    x= np.asarray( list(eneloss.keys()) ,  dtype=np.float32)
    y= np.asarray( list(eneloss.values()) , dtype=np.float32)
    
    #tcks = interpolate.interp1d(x, y, kind="linear")  # simple linear picture #
    tcks = interpolate.interp1d(x, y, kind="cubic")  # simple linear picture #
    #
    #====== I DONT CARE ABOUT B-SPLINES==========FROM NOW
    # #print( "INTERPOLATED",tck )
    # # splines:
    # tcks = interpolate.splrep( x, y, s=0)  # SPLINE FUNCTION 
    
    
    # ### plotting =======================
    # # 10e5 is enough to have smooth plot, but the function is important
    # xnew = np.linspace(x[0], x[-1], num=100000 , endpoint=True )
    # ynew = interpolate.splev(xnew, tcks, der=0)
    #plt.plot( x,y , '.', xnew, tck(xnew) ,'-')
    #plt.plot( x,y , '.', xnew, ynew ,'-' )
    
    if plot:
        Emin=min(tcks.x) # MeV
        Emax=max(tcks.x) # MeV
        unew = np.arange( Emin, Emax, 0.0001)
        out=tcks(unew)
        plt.plot(  x,y,'.',  label="losses")
        plt.plot( unew, out ,'-' , label="intep1d")
        plt.legend(  )
        plt.show()
    
    return tcks  # return spline function


#=====it was for b-splines not interp1d
# def get_interpolated_loss(x, tcks):
#     """
#     # stopping units  eV/ ( 1E15 atoms/cm2 )
#     """
#     resu=interpolate.splev(x, tcks, der=0)
#     return resu

# def get_interpolated_loss_inverse(x, tcks): # get splined values for X #
#     """
#     # stopping units  eV/ ( 1E15 atoms/cm2 )
#     - 1/S(E)  .... for integration
#     """
#     resu=-1.0*1E+15  / interpolate.splev(x, tcks, der=0)
#     return resu




def get_sr_loss( SRIN , Emax=5.8, dmax=10 , unit="um" ):
    print("\ni...       SRIN LOSS: Eini={}  t={} {}\n".format(Emax, dmax, unit) )
    if SRIN=="":
        print("XXX...   SR.IN was not created, returns")
        return
    eneloss,kevum,mevmg=run_sr_exe( SRIN )  # This returns loss tables BUT ALSO COEF!
    eneloss2=eneloss
    if unit=="um":
        for k in eneloss.keys():
            eneloss2[k]=eneloss[k]* kevum * 0.001
            #print(  "       --> ",eneloss[k] )
    if unit=="mg":
        for k in eneloss.keys():
            eneloss2[k]=eneloss[k]* mevmg
            #print(  "       --> ",eneloss[k] )
    #print("i...   SR.IN coef:  keV/um",kevum)  # keV/um for loss simulation
    #print("i...   SR.IN coef:  MeV/mg/cm2",mevmg)  #  for loss simulation
    
    tcks=srinterpolate( eneloss2 , plot=False)
    #============== integration
#    Emax=5.8
#    dmax=10.0 # um
    e=Emax
    dx=0.01  # 0.7um also gives good result to 4,5 digits
    dx=dmax/500
    x=0
    xs,es=0,Emax # added later
    while (x<dmax) and (e>0):
        xs,es=x,e
        if e>min(tcks.x):
            #e=e-0.001* tcks( e )*dx  # ticks[keV/um] => Emax[MeV]
            e=e- tcks( e )*dx  # ticks[MeV/um] => Emax[MeV]
        else:
            #e=e-0.001* tcks( min(tcks.x) )*dx  # ticks[keV/um] => Emax[MeV]
            e=e- tcks( min(tcks.x) )*dx  # ticks[MeV/um] => Emax[MeV]
        x=x+dx
        #print(x, e)
    print("last two steps : {} {}   {} {}".format(x,e,xs,es) )
    dde=(dmax-xs)*(es-e)/(xs-x)
    print("_"*30,"\n\nE_SRIN = {:.5g}\n".format( es+dde ) ,"_"*30 )
    # stopping units  eV/ ( 1E15 atoms/cm2 )   : 7  #== this may work for yield
 


    

print("i... module  sr  is being loaded", file=sys.stderr)
if __name__=="__main__":

    #ipath=srim.CheckSrimFiles()

    h1=nubase.isotope(1,1)  # incomming ion
    #h2=db.isotope(2,1)  # incomming ion
    
    TRIMIN,SRIN=srim.PrepSrimFile( ion=h1, energy=5.8, angle=0., number=100, mater='al27', thick=100, dens=-11  )
    
    print("=======================  calc  5.8MeV over 27mg/cm2 thickness ")
    get_sr_loss( SRIN , 5.8, 27 , unit="um") # mg/cm2 thickness
