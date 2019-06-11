#!/usr/bin/env python

import subprocess as s
import os
import glob
import sys
import json

import pypact as pp
import matplotlib.pyplot as plt
from numpy import diff  # derivative of list




def remove( f ):
    try:
        os.remove(f)
    except:
        print("-... file not exists for deletion:", f, file=sys.stderr)




def FISPACT_CALCULATE( COMMAND ):
    if (True):
        print("=======================CALCULATING=====================")
        print("======================= ",COMMAND,"=====================")
        print("=======================CALCULATING=====================")
        #res=s.check_output( [FISPACT, COMMAND ] ).decode("utf8").strip()
        res=s.check_call( [FISPACT, COMMAND ] )
        if res!=0:
            print("X... problem running", COMMAND)
            quit()


    
#
# as i understand:
#  files contains all
# 1 I run ficpact convert to convert from arb_flux to flux
# 2 compress,collaps..e
#
#  fispact inventory ! and take out the data
#



def dec_files(key):
    if key=="a2data":  s="A2 Transport data ... ../EAF2010data/eaf_a2_20100"
    if key=="absorp":  s="Absorption            ../EAF2007data/eaf_abs_20070"
    if key=="arb_flux":s="CHARGED SPECTRA DEFINITION     spectra"
    if key=="arrayx":  s="when GETDECAY 0 use the file: condensed_decay_and_fission_data"
    if key=="asscfy":  s="IF Actinides Fiss N/P/D   ../EAF2010data/eaf_n_asscfy_20100"
    if key=="clear":   s="CLEARANCE INDEX       ../EAF2010data/eaf_clear_20100"
    if key=="collapxi":s="file        collapsed_cross_section_dat"
    if key=="collapxo":s="file        collapsed_cross_section_data"
    if key=="crossec": s="x.s.  library N/P/D    ../EAF2007data/eaf_p_gxs_211_flt_20070"
    if key=="decay":   s="decay library          ../EAF2010data/eaf_dec_20100.001"
    if key=="fissyld": s="FISSION YIELD N/P/D    ../EAF2007data/eaf_n_fis_20070"
    if key=="fluxes":  s="SUMMARY_OF_SPECTRA-(Generated4charged)    flux"
    if key=="hazards": s="../EAF2010data/eaf_haz_20100"
    if key=="ind_nuc": s="../EAF2010data/eaf_index_20100"






    
#====================================================================
#                        START 
#====================================================================
        
FISPACT=s.check_output("which fispact".split() ).decode("utf8").strip()
print( FISPACT )


#
#============ check the existence of items in FILES
#
print("i... getting input:  files")
with open("files") as f:
    files=f.readlines()
files=[ i.strip() for i in files if len( i.strip())>1 ]
# remove comments
files=[ i.strip() for i in files if i.find("#")!=0 ]
DICTin={}
for i in files:
    DICTin[ i.split()[0] ]= i.split()[1]
#print( files )
print( json.dumps( DICTin, ensure_ascii = False, indent=4, sort_keys=True ) )
ok=True
for k,v in DICTin.items():
    if not os.path.isfile( v ):
        print("X... file/dir doesnt exist: ",k)
        if not k=="fluxes":
            ok=False
if not ok:
    quit()

    
#============== check the fluxes  spectrum:
with open(DICTin["arb_flux"]) as f:
    spectra=f.readlines()
spectra=[ i.strip() for i in spectra ]
spectra_label=spectra[-1]
spectra=spectra[:-2]
spectra=" ".join(spectra).split()
spectra=[ float(i) for i in spectra ]
# now I should go with bins down
bins=[]
vals=0
for i in spectra:
    if i>=0:
        bins.append(i/1e+6)
        vals+=1
    if i==0:
        break
#bins=diff(bins)/1.    
print(len(bins), vals , bins)
print("=============spectra values:")
spectra=spectra[vals:] # -1 is here to compensate for diff()/1
while len(spectra)>len(bins): #==== for deuterons ok
    spectra=spectra[:-1]
while len(spectra)<len(bins): #==== for neutrons i needed remove
    bins=bins[:-1]
    
print(len(spectra), spectra)
plt.figure(1)
plt.subplot(211)
plt.plot( bins, spectra , label="spectra: "+spectra_label )
plt.xlabel("[MeV]")
plt.yscale("log")
plt.legend()

#plt.show()

remove( DICTin["fluxes"] )
remove("convert.out")
FISPACT_CALCULATE( "convert" )



with open( DICTin["fluxes"] ) as f:
    flux=f.readlines()
flux=[ i.strip() for i in flux ]
flux=flux[:-2]
flux=" ".join(flux).split()
flux=[ float(i) for i in flux ]
#print(flux)
plt.subplot(212)
plt.plot( flux , label="recalculated flux: "+spectra_label )
plt.yscale("log")
plt.xlabel("bin")
plt.legend()

plt.tight_layout()
plt.show()











for fi in glob.glob("*.out"):
    remove( fi ) 
for fi in glob.glob("*.log"):
    remove( fi ) 

remove( DICTin["arrayx"]   ) #remove("rm condensed_decay_and_fission_data")
remove( DICTin["collapxi"] ) # remove("rm collapsed_cross_section_data")
remove( DICTin["collapxo"] ) # remove("rm collapsed_cross_section_data")
    





PP=0
DD=0
GG=0
AA=0
NN=0


INPS=( "convert.i", "collapse.i", "condense.i",  "inventory.i" )
for i in INPS:
    with open(i) as f:
        cont=f.readlines()
    cont=[ i.strip() for i in cont if i.find("PROJ")>=0]
    DD+=len(list(filter(lambda x: x=="PROJ 2", cont) ) )
    PP+=len(list(filter(lambda x: x=="PROJ 3", cont) ) )
    AA+=len(list(filter(lambda x: x=="PROJ 4", cont) ) )
    GG+=len(list(filter(lambda x: x=="PROJ 5", cont) ) )
    NN+=len(list(filter(lambda x: x=="PROJ 1", cont) ) )
    #print(i,cont)
    
print( "proton={} deuteron={} alpha={} gamma={} neutron={}".format( PP,DD, AA, GG, NN) )


#ok=False
#try:
#    with open("spectra") as f:
#        spe=f.readlines()
#    spe=[ i.strip() for i in spe ]
#    ok=True
#except:
#    print("X... no spectra file")
#if not ok: quit()
#print("SPECTRA: ",spe)


#================================ RUN FISPACT ====================
remove("collapse.out")
FISPACT_CALCULATE( "collapse" )
remove("condense.out")
FISPACT_CALCULATE( "condense" )
remove("inventory.out")
FISPACT_CALCULATE( "inventory" )
#if (True):
#    #res=s.check_output( [FISPACT,"convert"] ).decode("utf8").strip()
#    res=s.check_output( [FISPACT,"collapse" ]).decode("utf8").strip()
#    res=s.check_output( [FISPACT,"condense" ]).decode("utf8").strip()
#    res=s.check_output( [FISPACT,"inventory"] ).decode("utf8").strip()


#============================= get data from inventory
    
filename = "inventory.out"

with pp.Reader(filename) as output:
    # print JSON format to standard output
    #print(output.run_data)
    print(output.run_data.json_serialize())
    #print(output.inventory_data[0].json_serialize())
    #print(output.inventory_data[0].json_serialize())
    #for t in output.inventory_data:
    #    print("nuclides:",len(t.nuclides))
    olen=len(output)
    ttime=0
    isoact={} # i will keep over all
    for o in range(olen):
        irtime=output.inventory_data[o].irradiation_time
        cotime=output.inventory_data[o].cooling_time  # cooling time in sec.
        ttime=irtime+cotime
        
        isodict={}
        for nuc in output.inventory_data[o].nuclides:
            isotope=str(nuc.isotope)+nuc.state+nuc.element
            isodict[ isotope ]= nuc.activity
            if nuc.activity>1:
                if not isotope in isoact.keys():
                    #print("new key",isotope) 
                    isoact[ isotope ]=[]
                isoact[ isotope].append(  [ ttime/3600, nuc.activity ]  )
                
        lil=sorted( isodict.items(), key=lambda x: x[1] , reverse=True)
        act=""
        if len(lil)>0:
            #print( lil[0] )
            
            if lil[0][1]>1e+9:
                act=str(lil[0][1]/1e+9)+" GBq"
            if lil[0][1]>1e+6:
                act=str(lil[0][1]/1e+6)+" MBq"
            elif lil[0][1]>1e+3:
                act=str(lil[0][1]/1e+3)+" kBq"
            else:
                act=str(lil[0][1]/1e+0)+" Bq"
            act="{:4s}  {}".format(lil[0][0],act) # the most active element
                #print(   )
            
        print("{:2d} {:8.1f} h : {:12.3f} uSv/h     {} / ...{} ".format(o,ttime/3600, output[o].dose_rate.dose*1e+6 , irtime ,   act   ) )


#==================================== EXAMPLE DOESNT WORK..............        
# import pypact.analysis as ppa
# #isotopes = [ ppa.NuclideDataEntry(i) for i in ppa.getallisotopes() if ppa.findZ(i[0]) <= 10]
# isotopes=["H-1"]

# tz=ppa.TimeZone.COOL        
# with pp.Reader(filename) as output:
#     ppa.plotproperty(output=output,
#                      property='grams',
#                      isotopes=isotopes,
#                      plotter=plt,
#                      fractional=True,
#                      timeperiod=tz)

# plt.show()


#print( isoact )
for k,i in isoact.items():
    #print( k,"### ",i )
    plt.plot( *zip(*i)  , label=k  )
plt.xscale("log")
plt.yscale("log")
plt.xlabel('hours')
plt.legend()
plt.rc('grid', linestyle=":", color='black')
plt.grid()
plt.show()
#============================= READ OUTPUT ===========================    
print("\n----------------------------------------------------- mockup here")
uA=0.0
charge=0

if PP>2:  charge=1
if DD>2:  charge=1
if AA>2:  charge=2

with open("inventory.out") as f:
    inve=f.readlines()
inve=[ i.strip() for i  in inve]

meanflux=[ i for i in inve if i.find("Mean flux")>=0][0].split()[3]
meanflux=float(meanflux)
print( "mean current={:6.3f} uA".format(charge*meanflux*1.60217662e-19*1e+6 ) )


mass=[ i for i in inve if i.find("Mass of material")>=0][0].split()[6]
#print( "mass        ={}".format(mass ) )
mass=float(mass)*1000
if charge>0:
    print("Thickness   ={:9.3f} g/cm2".format( mass) )
else:
    print("Mass        ={} g".format( mass) )


totalactivity=[ i for i in inve if i.find("TOTAL ACTIVITY FOR ALL")>=0][0]
print( totalactivity)

totalirrad=[ i for i in inve if i.find("Total irradiation")>=0][0]
print( totalirrad)


quit()
###############################################################################








# #
# ################### only INITIAL COMPOSITION ?
# #
# batch=[]
# for i in inve:
#     if len(batch)>0: # trick
#         batch.append(i)
#     if i.find("ATOMS      GRAM-ATOMS     GRAMS")>=0:
#         batch.append(i)
#     if i.find("GAMMA SPECTRUM")>=0:
#         batch=batch[1:-1]
#         batch=[ j for j in batch if len(j)>0 ]
#         #print( batch , end="\n")
#         for j in batch:
#             z,el,abu=j.split()[0:3]
#             beta=j.split()[5]
#             gamma=j.split()[7]
#             alpha=j.split()[9]
#             print("{:2d} {:3s} {}    b-g-a: {}  {}  {} Curies-MeV".format( int(z),el,abu, beta, gamma , alpha)   )
#         print()
#         batch=[]





#
########################### SUMMARY OUTPUT
#
batch=[]
for i in inve:
    if len(batch)>0: # trick
        batch.append(i)
    if i.find("Summary Output")>=0:
        batch.append(i)
    if i.find("Mass of material input")>=0:
        batch=batch[1:-1]
        batch=[ j for j in batch if len(j)>0 ]
        #print( batch , end="\n")
        nadp1=batch[0].split()[2],batch[0].split()[3],batch[0].split()[4]+" "+batch[0].split()[5],batch[0].split()[6]+" "+batch[0].split()[7],batch[0].split()[8]+" "+batch[0].split()[9], batch[0].split()[10]+" "+batch[0].split()[11], batch[0].split()[12]+" "+ batch[0].split()[13]
        nadp2=batch[1].split()[1:]
        print( list(zip(nadp1,nadp2) ) )
        #print( nadp1 )
        #print(nadp2)
        for j in batch[2:]:
            k=j.split()
            # i remove cumulative years
            print( "\t".join(k[0:3]) ,"  ",   "\t".join(k[4:])  )
        print()
        batch=[]


