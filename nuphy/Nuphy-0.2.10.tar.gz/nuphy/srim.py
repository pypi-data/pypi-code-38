#!/usr/bin/env python3
import sys
sys.path.insert(0, '.') #  I PUT PRIORITY TO LOCAL DEVELOPMENT

import os
import tempfile   # create tempdir
import shutil     # rm tempdir, copytree NOT GOOD ENOUGH
import glob, os   # find file in directory
from distutils.dir_util import copy_tree  # copytree
import subprocess
from contextlib import contextmanager       # for CD with context
from xvfbwrapper import Xvfb  # invisible RUN
import math # isnan()

###from NuPhyPy.db.ReadNubase import gas,densities,elements
from nuphy.nubase import gas,densities,elements,molarweights
import nuphy.nubase as nubase
import nuphy.compounds as srcomp
###from NuPhyPy.db.ReadNubase import gas,densities,elements
###import NuPhyPy.db.readnubase as db


import threading
import time
import sys
#import compounds

#####from tqdm import *

#######3https://web-docs.gsi.de/~weick/atima/

TRIMAUTO="""1

TRIMAUTO allows the running of TRIM in batch mode (without any keyboard inputs).
This feature is controlled by the number in line #1 (above).
  0 = Normal TRIM - New Calculation based on TRIM.IN made by setup program.
  1 = Auto TRIM - TRIM based on TRIM.IN. No inputs required. Terminates after all ions.
  2 = RESUME - Resume old TRIM calculation based on files: SRIM Restore\*.SAV.

  Line #2 of this file is the Directory of Resumed data, e.g. A:\TRIM2\ 
  If empty, the default is the ''SRIM\SRIM Restore'' directory.

See the file TRIMAUTO.TXT for more details.
""";



#--- is ipython....
def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

def isjupyter():
    #print('D... checking JUPYTER')
#def in_ipynb():
#    try:
#        cfg = get_ipython().config
#        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
#            return True
#        else:
#            return False
#    except NameError:
#        return False
    '''
    isjupyter recognizes if run from Jupyter / IPython
    '''
    try:
        __IPYTHON__
        return True
    except:
        return False

###################################
#  this part should return to CUR DIR
#   after the context ends...
####################################
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


def CheckSrimFiles():
    '''
    I want to find installation of SRIM that i can copy to tmp
    '''
    home = os.path.expanduser("~")
    paths=[home]
    paths.append(home+'/srim/')
    paths.append(home+'/bin/srim/')
    paths.append(home+'/.wine/drive_c/Program Files/SRIM/')
    paths.append(home+'/.wine/drive_c/Program Files (x86)/SRIM/')
    # installation of NuPhyPy-------------
    MyPath= os.path.abspath(__file__)
    paths.append( os.path.dirname(MyPath)+'/srim_binary/rundir/'  )
    #
    #
    #
    #    print('i... checking PATH',  paths)
    RPATH=None
    for path in paths:
        if os.path.exists(path):
            #print('i... checking path ', path )
            for file in os.listdir( path ):
                if file=='TRIM.exe':
                    RPATH=path
                    print('+...  found SRIM.exe in ',path)
    if RPATH is None:
        print("X... srim not found in ",paths)
        print("X... TYPE       nuphy helpinstall")
        quit()
    return RPATH




##############################################
#
#      DATA READOUT

def srim_readout(temppath):
    '''
    returns list of relevant lines
    '''
    #print("D... SRIM READ FROM ",temppath)
    with cd(temppath):
        with open(r'SRIM Outputs/TRANSMIT.txt') as f:
            print("D... SRIM READ FROM ",temppath,r'SRIM Outputs/TRANSMIT.txt')
            cont=f.readlines()
            #f.close() #automatic
        while cont[0].find('Numb Numb')<0:
            cont.pop(0)
        cont.pop(0)
        #print("DEBUG DAT",cont)
        return [x.rstrip() for x in cont]

    
def srim_readout_range(temppath):
    with cd(temppath):
        with open(r'SRIM Outputs/RANGE_3D.txt' , 'rb' ) as f:
            cont=f.readlines()
            f.close()
        print('D... file is read')
        for i in range(13):
            cont.pop(0) # 1st 12 lines down
            ###print( 'LINEREM=',cont[0].decode('ascii', errors='ignore') )
        while cont[0].decode('utf8', errors='ignore').find('Number')<0 or cont[0].decode('utf8', errors='ignore').find('Angstrom')<0:
            cont.pop(0)
        print( 'LINEREM=',cont[0].decode('utf8', errors='ignore') )
        cont.pop(0)
        cont.pop(0)
        print( 'LINE=',cont[0].decode('utf8', errors='ignore') )
        return [x.decode('utf8', errors='ignore').rstrip() for x in cont]



def run_srim(RPATH, TRIMIN , strip=True, silent=False , nmax=1 ):
    '''
    This creates and environment in /tmp
    where TRIM.exe can be run
    TRIMIN contains all TRIM.IN text.
    strip... strip points above 3sigma
    '''
    if (RPATH is None):
        print("!...  SRIM.EXE not found.")
        print("i... try  nuphy.py helpinstall")
        quit()
    ############## CREATE TEMP #####################
    temppath = tempfile.mkdtemp( prefix='srim_')+'/'
    if not silent: print('X... copying from',RPATH,'to',temppath)
    copy_tree( RPATH , temppath )
#    os.chdir(temppath)
    #print('D...', glob.glob("TRIM.exe")  )
    ####################### IN CD CONTEXT #############
    with cd(temppath):
        #print('D...',glob.glob("TRIM.exe")  )
        for file in glob.glob("TRIM.exe"):
            if not silent: print('    : ',file)
        with open('TRIM.IN','w') as f:
            f.write( TRIMIN )
            f.close()
        with open('TRIMAUTO','w') as f:
            f.write( TRIMAUTO )
            f.close()
        if not silent: print('i...   TRIM.IN  and TRIMAUTO written')
        if isjupyter():
            print('i... JuPyter detected - vdislay initiated')
            silent=True #### PROBLEM with X in Jupyter?
#################################################### PROCESS WITH WAIT ####
        if silent:
            print("############### VDISPLAY #########################start")
            vdisplay = Xvfb(width=1280, height=740, colordepth=16)
            vdisplay.start()
        def worker():
            process = subprocess.Popen('wine TRIM.exe'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            output, error = process.communicate()
            return
        t=threading.Thread(target=worker)
        t.start()

        ###====>
        toolbar_width = 50
        if not is_interactive():
            sys.stdout.write("[%s]" % (" " * toolbar_width))
            sys.stdout.flush()
            sys.stdout.write("\b" * (toolbar_width+1)) # return to start after '['

        for i in range(84500):  # ONE DAY CHECK - just return number of lines
            destin=temppath+'/SRIM Outputs/TRANSMIT.txt'
            output = subprocess.check_output('wc -l '+destin+' 2>/dev/null | cut -d " " -f 1', shell=True).decode('utf8').rstrip()
            try:
                output=int(output)
            except:
                output=0
            ratio=output/nmax
            if ratio>1.0:ratio=1.0
            toolfull=int(toolbar_width*ratio)
            time.sleep(1)
            bar1="[%s" % ("#" * toolfull   )
            bar2="%s]%d/%d" % (" " * (toolbar_width-toolfull+0), output,nmax  )
            bar=bar1+bar2
            if not is_interactive():
                sys.stdout.write("\b" * (len(bar)+1)) # return to start a
                sys.stdout.write(bar)
                sys.stdout.flush()
            if not t.isAlive(): break
        ###========================>
        t.join()

        if silent:
            vdisplay.stop() #
            #print()
            print("\n############### VDISPLAY #########################stop")
#################################################### PROCESS WITH WAIT ####


#################################################### PROCESS NO WAIT ####
        #vdisplay = Xvfb(width=1280, height=740, colordepth=16)
        #vdisplay.start()
#        process = subprocess.Popen('wine TRIM.exe'.split())
        #print('CMD ended with string=',output,'... with error=',error)
        #vdisplay.stop() #
#################################################### PROCESS NO WAIT ####

#   return temppath
#def recollect_srim( temppath,  strip=True ):
    #import os
    #import time
    #vdisplay.stop()
    if not os.path.exists(temppath):
        print('!... Path',temppath,'DOES NOT EXIST !')
        return None
    #    os.chdir(temppath)
    with cd(temppath):
        if os.path.exists(r'SRIM Restore/TDATA.sav'):
            if not silent: print('ok')
        else:
            print('!... data not ready ',temppath,'... return')
            print('     can be:   Srim-Windows libraries not installed')
            print('     can do:   tar -xvzf libs2013.tgz  -C ~/.wine/drive_c/windows/')
            return None
    #
    data=srim_readout( temppath )
    # back with cd() =============================
    # I want to remove 1st column: T   :BUT above T 9999 it reads T10000
    # what if i replace T with space?
    data=[  'T '+x[1:] for x in data ]
    datas=[ (x.split()[1:]) for x in data ]
    datas=[ [ float(j) for j in i ] for i in datas ]
    # now i have list of list of floats : each line
    from pandas import DataFrame
    df = DataFrame(datas, columns=['n','i','e','x','y','z','cosx','cosy','cosz'])
    df['e']=df['e']/1000000.  # MeV
    df['x']=df['x']/10000.  # um
    df['y']=df['y']/10000.  # um
    df['z']=df['z']/10000.  # um
    #print( df.iloc[-5:][['e','x','y','z','cosx','cosy'] ] )
    df.drop('i', axis=1, inplace=True)
    df.drop('n', axis=1, inplace=True)
    if strip:
        llen=len(df)
        sigma=df['e'].std()
        mean=df['e'].mean()
        if math.isnan(sigma):
            sigma=mean
        print("DEBUG sigma=",sigma,"mean==",mean)
        df=df.loc[ (df['e']>mean-3*sigma)&(df['e']<mean+3*sigma) ]  #&
        if not silent:print('i... ',llen - len(df),'events were removed due to sigma limit' )
        sigma=df['e'].std()
        mean=df['e'].mean()
        if math.isnan(sigma):
            sigma=mean
        df=df.loc[ (df['e']>mean-3*sigma)&(df['e']<mean+3*sigma) ]  #&
        if not silent:print('i... ',llen - len(df),'event was removed due to sigma limit' )
    if len(df)<1 or  df['e'].mean is None:
        print("!... no transmited ions probably, i should check RANGE_3D.TXT")
        data=srim_readout_range( temppath )
        print('D... data read')
        datas=[ (x.split()[1:]) for x in data ]
        datas=[ [ float(j) for j in i ] for i in datas ]
        df = DataFrame(datas, columns=['x','y','z'])
        df['x']=df['x']/10000.  # um
        df['y']=df['y']/10000.  # um
        df['z']=df['z']/10000.  # um
        #print( df.iloc[-5:][['e','x','y','z','cosx','cosy'] ] )
        #df.drop('i', axis=1, inplace=True)
        #df.drop('n', axis=1, inplace=True)
        print("i... DEPTH= ",df['x'].mean,'um +- ',df['x'].std)
        ###########################  DELETE TEMP #########
    if not silent:print('x... deleting temporary', temppath)
    #shutil.rmtree(temppath)
    return df



# in perl:
#     - convolution with nehomogenities
#     - analyse range
#     - gpressTAB  STD    my $densNEW=$densSTD  *  $p/1013.25  *   273.15/$T;
#     -   if ( $args{"fthick"} >0){           amoeba







##################################################
#
#
#
###################################################


def PrepSrimFile( **kwargs ):
    '''
    thickness in  mg/cm2 from NOW
    '''
    SRLINE=[]
    OT=   proj( kwargs['ion'],kwargs['energy'],kwargs['angle'],kwargs['number'] , SRLINE)
    OT=OT+targ( kwargs['mater'],kwargs['thick'],kwargs['ion'],kwargs['dens'] ,    SRLINE)
    #print( SRLINE )
    if SRLINE!=[]:
        SRLINEOUTPUT= "\r\n".join(SRLINE)
        with open("/tmp/SR.IN","w") as f:
            f.write(  SRLINEOUTPUT+"\r\n" )
    else:
        SRLINEOUTPUT=""
    return OT,SRLINEOUTPUT




def proj( ion, energy, angle, number ,    SRLINE):
    seed=765
    ####  Z, Amu,  Energy,  Angle,  Number, BraggCorr, AutoNum
    ####   Z, Amu, BragggCor   #########3
    pro={'h1'  :[ 1, 1.00782503,  1.0 ],   #0.9570329
         'h2'  :[ 1, 2.014101777, 1.0   ] ,
         'h3'  :[ 1, 3.01604928 , 1.0   ] ,
         'he3' :[ 2, 3.01602,     1.0   ] ,
         'he4' :[ 2, 4.00260325,  1.0   ] ,
         'be9' :[ 4, 9.012,       1.0   ] ,
         'be10':[ 4, 10.01353382, 1.0   ] ,
         'b8'  :[ 5, 8.02460723,  1.0   ] ,
         'b10' :[ 5, 10.01293699, 1.0   ] ,
         'b11' :[ 5, 11.00930541, 1.0   ] ,
         'c12' :[ 6, 12.000,      1.0   ] ,
         'c13' :[ 6, 13.00335484, 1.0   ] ,
         'c14' :[ 6, 14.00324199, 1.0   ] ,
         'o14' :[ 8, 14.0086,     1.0   ] ,
         'o16' :[ 8, 15.995,      1.0   ] ,
         'f19' :[ 9, 18.9984,     1.0   ] ,
         'ne20':[ 10, 19.992440,  1.0   ] }

    if ion.namesrim in pro:
        #print('?...',ion.namesrim, '... PROJECTILE ALREADY DEFINED',pro[ion.namesrim])
        print('    ',ion.namesrim, '... PROJECTILE ALREADY DEFINED',pro[ion.namesrim])
    else:
        print(ion.namesrim,'not defined, I am defining it now')
        pro[ion.namesrim]=[ ion.Z, ion. amu, 1.0 ]    ## Bragg Corr i set to 1.0/C+C,h1+c,he4+c,
        print(ion.namesrim, 'DEFINED',pro[ion.namesrim])

    pro[ion.namesrim].insert( 2, energy*1000. )
    pro[ion.namesrim].insert( 3, angle )
    pro[ion.namesrim].insert( 4, number )    # N
    pro[ion.namesrim].append(  number-1 )     # AUTOSAVENUMBER

#    print( 'ION:',ion, pro[ion] )
    line1=' '+'   '.join(map(str,pro[ion.namesrim]))
    li2=[1, seed, 0]
    line2=' '+'   '.join(map(str,li2))
#    print(line1,line2)

    template_proj1="Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number."
    template_proj2="Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders"
    template_proj3="Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file"
    template_proj4="    1       0           1       0               0                               0"

    OUTTEXT=""
    OUTTEXT=OUTTEXT+'\r\n'
    OUTTEXT=OUTTEXT+template_proj1 +'\r\n'
    OUTTEXT=OUTTEXT+line1 +'\r\n'
    OUTTEXT=OUTTEXT+template_proj2 +'\r\n'
    OUTTEXT=OUTTEXT+line2 +'\r\n'
    OUTTEXT=OUTTEXT+template_proj3 +'\r\n'
    OUTTEXT=OUTTEXT+template_proj4 +'\r\n'

    
    #===================== SR.IN   must be unix \n, it is reverted later =======
    #SRLINE=[] # trick
    SRLINE.append("---Stopping/Range Input Data (Number-format: Period = Decimal Point)")
    SRLINE.append("---Output File Name")
    SRLINE.append('"OOOUTPUTFILE"')
    SRLINE.append("---Ion(Z), Ion Mass(u)")
    SRLINE.append("{}  {:.3f}".format( pro[ion.namesrim][0] , pro[ion.namesrim][1]  ) ) # Z,u
    #1   1.008)


    return OUTTEXT
#    print(OUTTEXT)
#    print('------- projectile done ------------')








############################################
#def targ(  name, thick,   ion,  outerdens=0.0  , SRLINE ):
def targ(  name, thick,   ion,  outerdens  , SRLINE ):
    '''
    thickness in mg/cm2 from NOW
    ...
    This should hadle now:
    li li6 li7 ... c c12 c13 c14
    ELEMENTAL TARGETS - if dens==0 : density from tables
    ISOTOPIC TARGETS  - if dens==0 : density calculated from elemental/molar_mass
    ... gaseous elements H,He,NOFNe...Ra / isotopes=simply by Z
    COMPOUNDS -  ??????
    !!! check CORRECT VALUES FOR BragCorr, indiv Displac/Latti/Surf !!!
    '''

#   heatsubl      indivdisp  latdispl ======= The data from SRIM for elements are here:
    heatsubl=[
       .00,
       .00,
       .00,
      1.67,
      3.38,
      5.73,
      7.41,
          2.00,
          2.00,
          2.00,
          2.00,
      1.12,
      1.54,
      3.36,
      4.70,
      3.27,
      2.88,
          2.00,
          2.00,
       .93,
      1.83,
      3.49,
      4.89,
      5.33,
      4.12,
      2.98,
      4.34,
      4.43,
      4.46,
      3.52,
      1.35,
      2.82,
      3.88,
      1.26,
      2.14,
           2.00,
           2.00,
       .86,
      1.70,
      4.24,
      6.33,
      7.59,
      6.83,
            2.00, #Tc
      6.69,
      5.78,
      3.91,
      2.97,
      1.16,
      2.49,
      3.12,
      2.72,
      2.02,
           2.00, #I
           2.00, #Xe
       .81,
      1.84,
      4.42,
      4.23,
      3.71,
      3.28,
           2.00, #Pm
      2.16,
      1.85,
      3.57,
      3.81,
      2.89,
      3.05,
      3.05,
      2.52,
      1.74,
      4.29,
      6.31,
      8.10,
      8.68,
      8.09,
      8.13,
      6.90,
      5.86,
      3.80,
       .64,  # Hg
      1.88,
      2.03,
      2.17,
      1.50,
           2.00,  #At
           2.00, #Rn
           2.00,
           2.00, #Ra
           2.00, #AC
      5.93,
           2.00, #Pa
      5.42 ]


    indivdisp=[
        0 ,
        10     ,
        5   ,
        25    ,
        25    ,
        25   ,
        28   ,
        28    ,
        28   ,
        25    ,
        5    ,
        25    ,
        25    ,
        25    ,
        15    ,
        25    ,
        25     ,
        25    ,
        5  ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        15   ,
        25    ,
        25   ,
        25   ,
        5    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        25    ,
        5   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25    ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25  ,
        25   ,
        25  ,
        25   ,
        25   ,
        25   ,
        25   ,
        25   ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25  ,
        25   ,
        25   ,
        25 ,
        25  ,
        25  ,
        25 ,
        25,
        25
        ]


    lattdisp=[
        0,
        3    ,
        1  ,
        3   ,
        3   ,
        3  ,
        3  ,
        3   ,
        3  ,
        3   ,
        1   ,
        3   ,
        3   ,
        3   ,
        2   ,
        3   ,
        3    ,
        3   ,
        1 ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        2  ,
        3   ,
        3  ,
        3  ,
        1   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        3   ,
        1  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3   ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3 ,
        3  ,
        3 ,
        3  ,
        3  ,
        3  ,
        3  ,
        3  ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3 ,
        3  ,
        3  ,
        3,
        3 ,
        3 ,
        3,
        3,
        3
        ]
    ####  Z, Amu,  Energy,  Angle,  Number, BraggCorr, AutoNum
    ####   Z, Amu, BragggCompCorr, indivDispl,  indivLattice, indivSurf==heatSubl
    mat={} # I NEED FOR ELEMENT
#     mat={#'li'          :[ 3,    6.941,     1.0,     25,      3,    1.67  ],
#          ########   prvky +  stoich,   CompoundBragg       density
#          'mylar'  : [{ 'h': 0.363636 },{ 'c': 0.454545 },{ 'o': 0.181818 }, 0.9570329,  1.397 ],
#          'ch2'    : [{ 'h': 0.666667 },{ 'c': 0.333333 }, 0.9843957 , 0.93  ],
#          'cd2'    : [{ 'h': 0.666667 },{ 'h2': 0.333333 }, 0.9843957 , 1.062857 ],
#          'lif'    : [{ 'li': 0.5 },{ 'f': 0.5 }, 1.0 , 2.635 ],
#          'cd2'    : [{ 'h': 0.666667 },{ 'h2': 0.333333 }, 0.9843957 , 1.062857 ],
# #         'havar'  : [{ 'c': 0.666667 },{ 'cr': 0.333333 }, 0.9843957 , 1.062857 ],
#          'melamin': [{ 'c': 0.2 },{ 'h': 0.4 },{ 'n': 0.4 }, 1.0 , 1.574 ],
#          'air'    : [{ 'c': 0.000124 },{ 'o': 0.231781 },{ 'n': 0.755268 }, { 'ar': 0.012827 },1.0,0.00120484 ],

#     #     'ar':[ 10, 19.992440,  0.0   ]
#     }



    #########################################
    #  heatsubl   indi lat displacement  and other data defined/introduced up to this point
    #
    #  NOW - find material/element/isotope
    #  mat[name]  will contain  eZ,amu  1. i,la,heatsu
    #
    #    AGAIN THE SAME ????????????? I DID IT ALREADY !!!!!
    isgas=-1
    #      compounds == No .title()
    #print("DDD>...",name, srcomp.material_text.keys())
    if name in srcomp.material_text.keys():     ###########################
        #==========  predefined materials HERE ===================
        if name in srcomp.material_gas: isgas=1  # "only Air"
        print('+...',name, '... MAT IS KNOWN and defined in compounds')
        # THIS CAN HAPPEN ONLY FOR COMPOUNDS NOW....................
        # replace  "HHHHH into MMMMM  WWWWW    DDDDD"
        ##OUTTEXT=srcomp.material_text[ name.title() ]
        OUTLIST=srcomp.rebuild( name )  # no title() for compounds
        #for i in OUTLIST: print(i)
        OUTTEXT="\r\n".join( OUTLIST )
        OUTTEXT=OUTTEXT.replace("HHHHH",  ion.namesrim )
        OUTTEXT=OUTTEXT.replace("MMMMM", name )
        if outerdens<=0.0:
            dens=srcomp.get_density( name )  # no .title() for compounds
        else:
            dens=outerdens
        OUTTEXT=OUTTEXT.replace("DDDDD", str(dens) )
        OUTTEXT=OUTTEXT.replace('WWWWW', str( 1000*thick/dens/1e-2  ) )  # in Angstr

        #print(OUTTEXT)
        #quit()
        print("DDD... returns compoud, no SRIN")
        while len(SRLINE)>0:
            SRLINE.pop(0)###### I cannot create SR.IN for compounds now.....
        return OUTTEXT  #################################################### COMPOUND RETURN HERE
    else:
        #print('DDD...',name,'MAT NOT defined ... ')
        if name.title() in elements:
            #print('+...',name.title(),'ELEMENT detected ... ')
            eZ=elements.index(name.title())
            isgas=gas[ eZ ]
            heatsu= heatsubl[eZ]
            #if isgas==1: heatsu=0.0
            mat[name]=[ eZ,molarweights[eZ], 1., indivdisp[eZ], lattdisp[eZ], heatsu ]
        else:
            #print('+...',name,'Isotope detected ... ')
            isotope=nubase.isotope( name )
            eZ=isotope.Z
            isgas=gas[ eZ ]
            heatsu= heatsubl[eZ]
            #if isgas==1: heatsu=0.0
            mat[name]=[ eZ, isotope.amu,  1., indivdisp[eZ], lattdisp[eZ],  heatsu ]

        #print('i...',name, 'MAT ... ',mat[name], '   "is gas"==',isgas)
        print('    ',name, '  "is gas"==',isgas)
        #print('!... ============= not correct ====== VERIFY INPUT in SRIM!')


    line=[]
    line.append("Target material : Number of Elements & Layers")
    line.append("\"HHHHH into MMMMM                     \"       1               1")
    line.append("PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]")
    line.append("       5                         0          0")
    line.append("Target Elements:    Z   Mass(amu)")
    #5
    line.append("Atom 1 = MMMMM =        ZZZZZ   AAAAA")
    line.append("Layer   Layer Name /               Width Density     MMMMM")
    line.append("Numb.   Description                (Ang) (g/cm3)    Stoich")
    line.append(" 1      \"MMMMM\"             WWWWW    DDDDD       1")
    line.append("0  Target layer phases (0=Solid, 1=Gas)")
    #10
    line.append("0")
    line.append("Target Compound Corrections (Bragg)")
    line.append(" 1")
    line.append("Individual target atom displacement energies (eV)")
    line.append("      25")
    #15
    line.append("Individual target atom lattice binding energies (eV)")
    line.append("       3")
    line.append("Individual target atom surface binding energies (eV)")
    line.append("    1.67")
    line.append("Stopping Power Version (1=2006, 0=2006)")
    #20
    line.append(" 0")
    line.append("")

    line[1]=line[1].replace('MMMMM', name )
    line[1]=line[1].replace('HHHHH', ion.namesrim )

    line[5]=line[5].replace('MMMMM', name )
    line[5]=line[5].replace('ZZZZZ', str(mat[name][0]) )
    line[5]=line[5].replace('AAAAA', str(mat[name][1]) )
    line[6]=line[6].replace('MMMMM', name ) # NEW - Be(4) -> to element

    # GET TABLE DENSITY
    if outerdens<=0.0:
#        print('i... density is given 0 - trying to find a rho for...',name.title())
        if name.title() in elements:
            CC=name.title()
            #print(CC,type(CC))
            zzz=elements.index(CC)
            #print(zzz)
            dens=densities[ elements.index(name.title() ) ]
            #print('i... element ',name.title(),'found, density is set to:', dens)
            print('        ',name.title(),'found, density is set to:', dens)
        else:
            #print('i... element NOT found, maybe it is an isotope?')
            isotope=nubase.isotope( name )
            dens=isotope.isodensity
            #print('i...  isotope:',isotope.name,'found;  density is set to:',dens)
            print('        ',isotope.name,'found;  density is set to:',dens)
    else:
        dens=outerdens

    
    #SRLINE=[] # i cannot do compound here
    SRLINE.append("---Target Data: (Solid=0,Gas=1), Density(g/cm3), Compound Corr.")
    #0    2.702    1)
    SRLINE.append("{}   {:.4f}  {}".format(isgas , dens  , 1 ) ) # gas, dens, compouncorr
    SRLINE.append("---Number of Target Elements")
    #1 )
    SRLINE.append("{}".format(1 )  ) # number of target elements 1 here
    SRLINE.append("---Target Elements: (Z), Target name, Stoich, Target Mass(u)")
    #13   "Ablb"              1             26.982)
    SRLINE.append('{}  "{}"  {}  {}'.format(mat[name][0], name, 1, mat[name][1]  ) ) # Z , name , stoich==1  u(mass)
    SRLINE.append("---Output Stopping Units (1-8)")
    SRLINE.append(" 7")
    SRLINE.append("---Ion Energy : E-Min(keV), E-Max(keV)")
    SRLINE.append(" 10    50000")

    #======================= I AM DONE WITH SR.IN for isotope or element================
    
    
    line[8]=line[8].replace('DDDDD', str(dens) )
    #um_thickness * rho
    print('i... Thickness: {:.5f} mg/cm2 ==> {:.3f} um'.format( thick, 1000*thick/dens/1e+2 )  )
    #line[8]=line[8].replace('WWWWW', str(thick*10000.) ) # thickness will be ug/cm2 in future
    line[8]=line[8].replace('WWWWW', str( 1000*thick/dens/1e-2  ) )  # in Angstr
    line[8]=line[8].replace('MMMMM', name )


    if isgas>0:
        print('!... ASSUMING GASEOUS material:', name.title() )
        line[10]=line[10].replace('0', str( isgas) )  # SOILID 0,  GAS 1

    line[12]=str(mat[name][2])  # BragCorr 1.0
    line[14]=str(mat[name][3])  # indivDsplacement 25-28
    line[16]=str(mat[name][4])  # indivLatice  3
    line[18]=str(mat[name][5])  # indivSurf    1.67-7.41

    OUTTEXT=""
    for i in range(len(line)):
        OUTTEXT=OUTTEXT+line[i] +'\r\n'

    return OUTTEXT
#    print( OUTTEXT )
#    print('------- target done ------------')
#############################################################################




#######  um to  mg/cm2   and back ######
def get_mgcm2(t_in_um,  dens):
    return t_in_um*1e-6 * 100 * dens*1000
def get_um(t_in_mgcm2,  dens):
    return 1000*t_in_mgcm2/dens/1e+2








#########################################################
# MAIN
#########################################################
#sys.modules[__name__]
print("i... module  srim  is being loaded", file=sys.stderr)
if __name__ == "__main__":
#    print("running ",sys.modules[__name__],"as main")
    print("running ",__file__,"as main")
    ipath=CheckSrimFiles()
#    import NuPhyPy.db.ReadNubase as db
#    alpha=db.isotope(4,2)
#    c12=db.isotope(12,6)
    h1=nubase.isotope(1,1)  # incomming ion
    TRIMIN,SRIN=PrepSrimFile( ion=h1, energy=5.8, angle=0., number=100, mater='c12', thick=10, dens=1.85  )
    #####? create_env(ipath)
    print("------------ TRIMIN PREPARED -----------------------------")
    print(TRIMIN)
    print("------------ TRIMIN PREPARED -----------------------------")
    run_srim(ipath, TRIMIN,  silent=False, nmax=100)
