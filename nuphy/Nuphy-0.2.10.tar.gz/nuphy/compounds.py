import re

############################################
# COMPOUND MATERIALS
############################################
"""
 This will contain materials in directory:
    original text directly from SRIM
    rebuilt by autoatic procedure...
 AT THE MOMENT - PROBLEM WITH LAYERS
 - density etc....
  First letter uppercase : Title
"""


################################# DEFINITIONS
material_gas=['air']
material_text={}

####################################################
#
####################################################
material_text['air']="""==> SRIM-2013.00 This file controls TRIM Calculations.
Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.
     1   1.008         10       0     111        1    10000
Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders
                      1                                   0       0
Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file
                          0       0           0       0               0                               0
Target material : Number of Elements & Layers
"H (10) into                             "       4               1
PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]
       0                         0          100000
Target Elements:    Z   Mass(amu)
Atom 1 = C =         6  12.011
Atom 2 = O =         8  15.999
Atom 3 = N =         7  14.007
Atom 4 = Ar =       18  39.948
Layer   Layer Name /               Width Density      C(6)    O(8)    N(7)  Ar(18)
Numb.   Description                (Ang) (g/cm3)    Stoich  Stoich  Stoich  Stoich
 1      "Air, Dry (ICRU-104)"           100000  .00120484  .00015 .210756 .784423 .004671
0  Target layer phases (0=Solid, 1=Gas)
1
Target Compound Corrections (Bragg)
 1
Individual target atom displacement energies (eV)
      28      28      28       5
Individual target atom lattice binding energies (eV)
       3       3       3       1
Individual target atom surface binding energies (eV)
    7.41       2       2       2
Stopping Power Version (1=2011, 0=2011)
 0
"""




####################################################
#
####################################################
material_text['havar']="""==> SRIM-2013.00 This file controls TRIM Calculations.
Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.
     1   1.008         10       0     111        1    10000
Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders
                      1                                   0       0
Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file
                          0       0           0       0               0                               0
Target material : Number of Elements & Layers
"H (10) into Layer 1                     "       8               1
PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]
       0                         0          100000
Target Elements:    Z   Mass(amu)
Atom 1 = C =         6  12.011
Atom 2 = Cr =       24  51.996
Atom 3 = Mn =       25  54.938
Atom 4 = Fe =       26  55.847
Atom 5 = Co =       27  58.933
Atom 6 = Ni =       28   58.69
Atom 7 = Mo =       42   95.94
Atom 8 = W =        74  183.85
Layer   Layer Name /               Width Density      C(6)  Cr(24)  Mn(25)  Fe(26)  Co(27)  Ni(28)  Mo(42)   W(74)
Numb.   Description                (Ang) (g/cm3)    Stoich  Stoich  Stoich  Stoich  Stoich  Stoich  Stoich  Stoich
 1      "Havar (ICRU-470)"           100000  8.3 .009648 .222858 .016874 .181139 .417829 .128336 .014494 .008824
0  Target layer phases (0=Solid, 1=Gas)
0
Target Compound Corrections (Bragg)
 1
Individual target atom displacement energies (eV)
      28      25      25      25      25      25      25      25
Individual target atom lattice binding energies (eV)
       3       3       3       3       3       3       3       3
Individual target atom surface binding energies (eV)
    7.41    4.12    2.98    4.34    4.43    4.46    6.83    8.68
Stopping Power Version (1=2011, 0=2011)
 0
"""


####################################################
#
####################################################
material_text['mylar']="""==> SRIM-2013.00 This file controls TRIM Calculations.
Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.
     1   1.008        1000       0   99999 .9570329    10000
Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Reminders
                      1                                   0       0
Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Ion;2=Ion+Recoils), Special EXYZ.txt file
                          0       0           0       0               0                               0
Target material : Number of Elements & Layers
"H (10) into Layer 1                     "       3               1
PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]
       0                         0         1000000
Target Elements:    Z   Mass(amu)
Atom 1 = H =         1   1.008
Atom 2 = C =         6  12.011
Atom 3 = O =         8  15.999
Layer   Layer Name /               Width Density      H(1)    C(6)    O(8)
Numb.   Description                (Ang) (g/cm3)    Stoich  Stoich  Stoich
 1      "Mylar"           1000000  1.397 .363636 .454545 .181818
0  Target layer phases (0=Solid, 1=Gas)
0
Target Compound Corrections (Bragg)
 .9570329
Individual target atom displacement energies (eV)
      10      28      28
Individual target atom lattice binding energies (eV)
       3       3       3
Individual target atom surface binding energies (eV)
       2    7.41       2
Stopping Power Version (1=2011, 0=2011)
 0
"""



####################################################
#
####################################################
material_text['mgo']="""==> SRIM-2013.00 This file controls TRIM Calculations.
Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.
     1   1.008         10       0     111        1    10000
Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Remind$
1                                   0       0
Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Io$
                          0       0           1       0               0        $
Target material : Number of Elements & Layers
"H (10) into Layer 1                     "       2               1
PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]
       0                         0           10000
Target Elements:    Z   Mass(amu)
Atom 1 = O =         8  15.999
Atom 2 = Mg =       12  24.305
Layer   Layer Name /               Width Density      O(8)  Mg(12)
Numb.   Description                (Ang) (g/cm3)    Stoich  Stoich
 1      "MgO"           10000  3.576      .5      .5
0  Target layer phases (0=Solid, 1=Gas)
0
Target Compound Corrections (Bragg)
 1
Individual target atom displacement energies (eV)
      28      25
Individual target atom lattice binding energies (eV)
       3       3
Individual target atom surface binding energies (eV)
       2    1.54
Stopping Power Version (1=2011, 0=2011)
 0
"""





####################################################
#
####################################################
material_text['mg26o']="""==> SRIM-2013.00 This file controls TRIM Calculations.
Ion: Z1 ,  M1,  Energy (keV), Angle,Number,Bragg Corr,AutoSave Number.
     1   1.008         10       0     111        1    10000
Cascades(1=No;2=Full;3=Sputt;4-5=Ions;6-7=Neutrons), Random Number Seed, Remind$
1                                   0       0
Diskfiles (0=no,1=yes): Ranges, Backscatt, Transmit, Sputtered, Collisions(1=Io$
                          0       0           1       0               0        $
Target material : Number of Elements & Layers
"H (10) into Layer 1                     "       2               1
PlotType (0-5); Plot Depths: Xmin, Xmax(Ang.) [=0 0 for Viewing Full Target]
       0                         0           10000
Target Elements:    Z   Mass(amu)
Atom 1 = O =         8  15.999
Atom 2 = Mg =       12 25.9826
Layer   Layer Name /               Width Density      O(8)  Mg(12)
Numb.   Description                (Ang) (g/cm3)    Stoich  Stoich
 1      "MgO"           10000  3.725      .5      .5
0  Target layer phases (0=Solid, 1=Gas)
0
Target Compound Corrections (Bragg)
 1
Individual target atom displacement energies (eV)
      28      25
Individual target atom lattice binding energies (eV)
       3       3
Individual target atom surface binding energies (eV)
       2    1.54
Stopping Power Version (1=2011, 0=2011)
 0
"""











def rebuild( matname):
    """
    material_text is already definede above:
    the task here is only to change few parameters......
    .... like thickness, density
    """
    INTEXT=material_text[ matname ].split('\n')
    line=[]
    flag=False
    for l,v in enumerate(INTEXT):
        #print(l,'/',v)
        if v.find('Target material')>=0:
            flag=True
        if flag:
            line.append(v)
    # replace  "HHHHH into MMMMM  WWWWW    DDDDD"
    line[1]=re.sub( '".+"', '"HHHHH into MMMMM"',  line[1] )
    # std outputline
    line[3]="       5                         0          0"
    # taget elements lie - could be 3 for mylar
    for l,v in enumerate(line):
        if v.find('g/cm3')>0:
            #print(l,"LINE",v)
            break
    lineDens=re.findall(r'([\w\d\.]+|".*?")', line[l+1])
    print("D...",lineDens)
    ########lineDens=line[l+1].split()
    lineDens[2]='WWWWW'
    lineDens[3]='DDDDD'
    line[l+1]=" "+"    ".join( lineDens )
    #print(lineDens)
    return line


###########density
def get_density( matname ):
    INTEXT=material_text[ matname ].split('\n')
    #print('D... in get density')
    line=""
    for l,v in enumerate(INTEXT):
        #print(l,v)
        if v.find('g/cm3')>0:
            line=INTEXT[l+1]
            break
    print('F... ',line)
    dens=re.findall(r'([\w\d\.]+|".*?")', line)[3].strip()
    #####dens=line.strip().split()[3]
    return float(dens)
