#!/usr/bin/env python3




def HELP_REACT():
    print("""
help for reactions:
   REACTIONS:========================================

usage:  nuphy -i incoming,target -o outgoing -e energyMeV -a outgoingAngle


   nuphy  react  -i h2,c12  -o h1  -e 19  -a 11

   nuphy react -i h2,h1 -o he3

   # excitation energy of 1.23 MeV:
   nuphy react -i h2,c12 -o h1 -e 12 -x 1.23

   # to save T3 into a text file for later scripting:
   nuphy react -i h2,c12 -o h2 -e 22 -a 10 -S aaa.txt,T3
   nuphy react -i h2,c12 -o h2 -e 22 -a 10 -S aaa.txt,T3a
   nuphy react -i h2,c12 -o h2 -e 22 -a 10 -S aaa.txt,T3b

""")


def HELP_STORE():
    HELP_SRIM()
    print("""
           -S option has a special meaning for
    react  :   -S aaa.txt,T3a    ... saves the value to aaa.txt
   rrate   :
""")

def HELP_RRATE():
    print("""
   Reaction Rates: ==================================== rrate:

                   current        xs in [barns]   thickness  material  SolidAngle [Sr]")
            rrate -n 10uA -i h1  -cs 0.035       -t 10um    -m c12    -a 0.000177
                                                        6mm2 / (184mm)^2 = 1.7722-4 Sr")
   nuphy rrate -i h1 -m c12 -n 1uA -cs 0.1 -t 100um -a $((6./180))

   nuphy rrate -n 10nA -cs 0.035 -t 1um -m cu63 -a 0.00017
                   # -a ... solid angle:  for rect. slit= x*y/R^2

   Reaction Rates: ==================================== TENDL + SRIM losses
                                                          TENDL (h1 ... he4)
   nuphy react -i h2 -m c12 -o c11 --tendl  -g  # show graphs
   nuphy rrate -i h1 -m c12 -o c11 -n 1uA -cs 0.1 -e 16,11 -t 100um -a $((6./180)) -tendl

    4 rrate only:   -cs   -t  (xs and thickness)
    4 TENDL:        -cs and -t not needed;  -tendl ( -tendl tot. -tendl L00, -tendl L01 )
             rrate -i h1 -m mg26 -o al26 -n 1uA -e 16,15  -tendl -g
             rrate -i h2 -m mg26 -o al26 -tendl L00  -e 75,20 -g


""")


    
def HELP_SRIM():
    print("""
SRIM:=============================================
   nuphy  srim   -i h1 -m si -e 28 -f 0.0001 -t 55um -n 100 -s -S ~/srim_data.hdf5

Plotting SRIM from hdf5 file:=======================
   nuphy  hdf5  -S ~/srim_data.hdf5,0  -g e -f 0.022


SRIM MODE runs srim.exe in /tmp and collects the statistics:
------------------------------------------------------------
   it can run calculation for
        -  elements
        -  isotopes
        - predefined materials - !  use exact Uppercas/lowercas letters !

understands um, mm and ug/cm3
   nuphy  srim   -i h1  -m si  -e 28    -t 5500um -n 500
   nuphy  srim   -i h1  -m si  -e 28    -t  5.5mm -n 500
   nuphy  srim   -i he4 -m c   -e 5.804 -t  100ug -n 500
   nuphy  srim   -i he4 -m c12 -e 5.804 -t  100ug -n 500
   nuphy  srim   -i he4 -m c14 -e 5.804 -t  100ug -n 500

uderstands density:
   nuphy  srim   -i he4 -m c -d 1.85  -e 5.804 -t 100um -n 500

understands pre-defined materials (test)
   nuphy  srim   -i he4 -m air   -e 5.804 -t  100ug -n 500

understands pressure [mbar] and temperature [K] of gas (test)
(default=STD (273.15 K, 1013kPa))
   nuphy srim -i h1 -e 20 -t 100000um -m h2 -P 1013000
   nuphy srim -i h1 -e 20 -t 100000um -m h2 -P 1024 -T 273

understands layers  (test)
    nuphy  srim   -i he4 -m c,si   -e 5.804 -t  50ug,50ug -n 500
    nuphy  srim   -i he4 -t 184ug,200ug,10000um,231231um -m havar,mylar,air,n14 -n 400 -P 150  -e 5.8  -S ~/store.hdf5



STORE events in a file:
   nuphy  srim   -i he4 -m c   -e 5.804 -t 100ug  -n 500 -S ~/srim_store.hdf5

LIST:  look what is stored in *.hdf5
   nuphy  hdf5 -S ~/srim_store.hdf5

   :from *.hdf5  (lines 0 and 1)
   nuphy  hdf5 -S ~/srim_h1h2,0,1
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -f 0.100
PLOT:      graph plots
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g e          #
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g dee -f 0.1 # de vs. E  noise 100keV
   nuphy  hdf5 -S ~/srim_h1h2,all -g yz         # all
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g [x|y|z]
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g [cos|cosy|cosz]
   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g view
""")

#    print("Materials pre-defined:")
#    for i in sorted(srcomp.material_text.keys()) : print("   ",i)








# replacing 8xv
#print('---------version: vvvvvvvv ---------------------------------');
#print('You entered nuphy, merger of calc-react and srimbuster');
# print("""
# Three MODES:
#   nuphy  react  -i h2,c12  -o h1  -e 19  -a 11
#   nuphy  srim   -i h1 -m si -e 28 -t 5500um -n 100
#   nuphy  srim   -i he4 -m c  -e 5.804 -t 100ug -n 100
# STORE in file:
#   nuphy  srim  -i he4 -m c  -e 5.804 -t 100ug -n 100 -S ~/srim_h1h2
#  LIST:
#   nuphy  hdf5 -S ~/srim_h1h2
#  PLOT
#   nuphy  hdf5 -S ~/srim_h1h2,0,1
#   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g yz
#   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g x
#   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g cos
#   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g cosy
#   nuphy  hdf5 -S ~/srim_h1h2,0,1 -g 0.100
#  RRATE:
#   nuphy  rrate -n 10nA  -t 10ug          -m c   -xs 0.1
#   nuphy  rrate -n 10uA  -t 10um   -d 1.8 -m c   -xs 0.1
#   nuphy  rrate -n 1uA   -t 100ug         -m h2  -xs 0.1
#   ...  ... current Nb/t;  rho_S;  Na/Mm ;  100mb=> R
# """)
# print("""
# MODES available:  react, srim, hdf5 (see srim), rrate
#    nuphy  react  -i h2,c12  -o h1  -e 19  -a 11
#    nuphy  srim   -i h1 -m si -e 28 -t 5500um -n 100 -s -S ~/srim_data.hdf5
#    nuphy  hdf5  -S ~/srim_data.hdf5,0,1
#    nuphy  rrate  -n 10nA  -t 10ug          -m c   -xs 0.1
# """)
