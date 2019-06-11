#!/usr/bin/env python
#import nuphy.nubase.nubase

#print("i... main  nuphy  is being run") ok





import nuphy.compounds as srcomp

from nuphy.nubase import gas,densities,elements,molarweights

import  nuphy.sr as sr
import  nuphy.srim as srim

###############################################################  SRIM
#
#  srim    -  first functions -
#
###############################


######################################
# look for compounds/elements/isotopes : return tabulated density
#
######################################
def material_density( matnam ):
    """
    called TWICE in the program:  returns  density, mm_amu
    if not material and not element => it could be isotope:
    """
    #print('i... testing if ',matnam,'is in compounds ')
    #print('DDD...  compounds keys: ',srcomp.material_text.keys()  )
    mm_amu=1.0  # NONSENSE
    isotope=None
    if matnam in srcomp.material_text.keys():
        print('F... FOUND in compounds')
        dens=srcomp.get_density( matnam  )
        print('i... FOUND density from compounds=',dens)  # mm_amu ???
        # mm_amu determined probably somewhere in SRIM.... # i dont need
    elif matnam.title() in elements:   # ELEMENT ARE AWAYS Capitalized
        print('F...  ',matnam,' FOUND in elements ')
        CC=matnam.title()
        #print(CC,type(CC))
        zzz=elements.index(  matnam.title() )
        #print(zzz)
        dens=densities[ elements.index( matnam.title() ) ]
        mm_amu=molarweights[  elements.index( matnam.title() ) ]  # Mm for mix of isotopes
        print('i... element ',matnam.title() ,'found, density is set to:', dens)
    else:
        #print('i... @material_density; element NOT found, maybe it is an isotope?')
        isotope=db.isotope( matnam.title() )
        if isotope.Z<0:
            quit()
        dens=isotope.isodensity
        mm_amu=isotope.amu   # This is for cross sections  Mm pure
        #
        #  COULD BE SOME CATCH HERE!!!!!!!! I REMOVED PRINTLINE
        #
        #print( isotope,isotope.Z, isotope.name , isotope)
        print('        isotope density set {:.4f} g/cm3'.format(dens) )
    return dens,mm_amu,isotope


##################
#  question on GAS = we use 2x
#################
def isitGas( material ):
    if material.title() in srcomp.material_gas:
        return 1
    if material.title() in elements:
        eZ=elements.index(material.title())
        if gas[ eZ ]==1:
            return 1
    try:
        print("i... is is gas - isotope")
        isotope=db.isotope( material , silent=True  )
    except:
        return 0
    if isotope==None:
        eZ=isotope.Z
        if gas[ eZ ]==1:
            return 1
    return 0





#####################################
# get_thick_rho  ......  I extract the part
#         return   thick [ug/cm2] and rho g/cm3
#####################################
def get_thick_rho( material,  thick, rho ):   #convert properly um and find rho
    """
    takes all thicknesses   um  ug:

    returns:  thickness,  rho, MM_amu

    1. a/ rho is given => ok,
       b/ rho not given => call material density; find rho,mm_amu

    for this it is necessary to create isotope
    """
    #print('D... in  get_thick_rho ::: DUPLICITE CODE:', material, thick, rho, '-------------')
    rho=float(rho)
    isotope=None
    mm_amu=0.0
    #print("i... @ get_thick_rho start")
    # i need rho(maybe; amu(for rrate)
    #print("*** ***")
    rho1,mm_amu,isotope=material_density(material) # compound/element/isot = ALL
    if rho==0:
        rho=rho1

    # GASEOUS DENSITY
    # 1/ if compound - rho from function
    # 2/ element:
    rho2=rho # to keep if solid phase

    #========test gas phase =========
    #print("***testgas")
    if material.title() in srcomp.material_gas:
        """
        trim assumes the target as STP before 1982
        T=273.15 K
        p=1013.25 kPa
        SRIMHelp/helpTR23.rtf
        """
        R=1013.25e+3/273.15/rho
        rho2=args.Pressure/R/args.Temperature
        print('i...rho at STD (0deg,1013kPa)=',rho,' NEW now=',rho2)
    elif material.title() in elements:
        #print("D... rho - elements")
        eZ=elements.index(material.title())
        print("D... rho - elements  eZ={:d}".format(eZ))
        #print(gas)
        if gas[ eZ ]==1:
            R=1013.25e+3/273.15/rho
            rho2=args.Pressure/R/args.Temperature
            print('i...rho at STD (0deg,1013kPa)=',rho,' NEW now=',rho2)
    else: # could be also a gaseous  isotope
        #print('D... maybe gaseous isotope?')
        if isotope is None:
            try:
                print("i... @ get_thick_rho  function")

                isotope=db.isotope( material , silent=True )
            except:
                 isotope=None
        if isotope==None:
            print('D... not a gaseous isotope')
        else:
            eZ=isotope.Z
            if gas[ eZ ]==1:
                print('i... GAS')
                R=1013.25e+3/273.15/rho
                rho2=args.Pressure/R/args.Temperature
                print('i...rho at STD (0deg,1013kPa)=',rho,' NEW now=',rho2)
    rho=rho2
    #print("D... rho WAS deduced")
    # THICKNESS TO mgcm2:    ##### MY UNIT WILL BE mg/cm2

    thickok=False
    if thick.find('ug')>0:
        thick=float(thick.split('ug')[0])/1000
        thickok=True
    elif thick.find('mg')>0:
        thick=float( thick.split('mg')[0] )
        thickok=True

    elif thick.find('um')>0:
        #print('   i... um ! I use rho=',rho)
        thick=float(thick.split('um')[0])
        thick=srim.get_mgcm2( thick,  rho ) # um in, mgcm2 out
        thickok=True
    elif thick.find('mm')>0:
        #print('   i... mm ! I use rho=',rho)
        thick=float(thick.split('mm')[0])
        thick=srim.get_mgcm2( thick*1000,  rho ) # um in, mgcm2 out
        thickok=True
    elif thick.find('cm')>0:
        #print('   i... cm ! I use rho=',rho)
        thick=float(thick.split('cm')[0])
        thick=srim.get_mgcm2( thick*10000,  rho ) # um in, mgcm2 out
        thickok=True

    if not(thickok):
        print('X...  thicknesses must be in ug,mg or um,mm')
        quit()
    #print('i... {} thickness {:.6f} mg/cm2 for rho={:.3f} ... {:.0f} A = {:.2f}um'.format( material.title(),thick,
    #                                            rho,1000*thick/rho/1e-2  ,   1000*thick/rho/1e+2 ) )
    print('         {} : {:.6f} mg/cm2 (rho={:.3f}) '.format( material.title(),thick, rho) )
    return thick, rho, mm_amu








######################################
#PREPARE TRIMIN
#  prepare single layer, return one TRIM.IN line
#     
#
#            prasarna  ......... incomming0
########################################
def prepare_trimin( material,  thick,  rho  , incomming0 , Eini, angle, number):
    '''
    Here I prepare materials:  single layers
    '''
    print('D... preparing TRIMIN:', material, thick, '  rho_ini=',rho, '-------------')
    #print('D... PV/T density:')
    rho=float(rho)
    isotope=None
    if rho==0:
        rho,mm_amu,isotope=material_density(material) # compound/element/isot = ALL
        #print("DDD...  rho_fromtables=", rho)
    # GASEOUS DENSITY
    # 1/ if compound - rho from function
    # 2/ element:
    rho2=rho # to keep if solid phase
    #print("DDD .... items of material_gas", srcomp.material_gas ) #"Air" only
    if material in srcomp.material_gas:
        """
        trim assumes the target as STP before 1982
        T=273.15 K
        p=1013.25 kPa
        SRIMHelp/helpTR23.rtf
        """
        R=1013.25e+3/273.15/rho
        rho2=args.Pressure/R/args.Temperature
        print('i...rho at STD (0deg,1013kPa)=',rho,' NEW now=',rho2)
    elif material.title() in elements:
        print("D... rho - elements")
        eZ=elements.index(material.title())
        print("D... rho - elements  eZ=",eZ)
        if gas[ eZ ]==1:
            R=1013.25e+3/273.15/rho
            rho2=args.Pressure/R/args.Temperature
            print('i...rho at STD (0deg,1013kPa)=',rho,' now=',rho2)
    else: # could be also a gaseous  isotope
        #print('D... maybe gaseous isotope?')
        try:
            isotope=db.isotope( material , silent=True )
        except:
            isotope=None
        if isotope==None:
            print('D... not a gaseous isotope')
        else:
            eZ=isotope.Z
            if gas[ eZ ]==1:
                print('i... GAS')
                R=1013.25e+3/273.15/rho
                rho2=args.Pressure/R/args.Temperature
                print('i...rho at STD (0deg,1013kPa)=',rho,' now=',rho2)
    rho=rho2

    #print("DDD... rho deduced")============================================
    # THICKNESS TO mgcm2:    ##### MY UNIT WILL BE mg/cm2
    thickok=False
    if thick.find('ug')>0:
        thick=float(thick.split('ug')[0])/1000
        thickok=True
    elif thick.find('mg')>0:
        thick=float( thick.split('mg')[0] )
        thickok=True
    elif thick.find('um')>0:
        print('i...  thickness in [um] ==> I use rho=',rho)
        thick=float(thick.split('um')[0])
        thick=srim.get_mgcm2( thick,  rho ) # um in, mgcm2 out
        thickok=True
    elif thick.find('mm')>0:
        print('i... thickness in [mm] ==> I use rho=',rho)
        thick=float(thick.split('mm')[0])
        thick=srim.get_mgcm2( thick*1000,  rho ) # um in, mgcm2 out
        thickok=True
    if not(thickok):
        print('!...  thicknesses must be in ug,mg or um, mm')
        quit()
    # INFO:
    print( "DDD... rho=",rho )
    print('i... {} thickness {:.6f} mg/cm2 for rho={:.3f} ... {:.0f} A = {:.2f}um'.format( material, thick,
                                                rho,1000*thick/rho/1e-2  ,   1000*thick/rho/1e+2 ) )

    # AT THIN MOMENT I HAVE A GOOD rho an thick in mgcm2

    #print('DDD... goto PrepSrimFile')
    TRIMIN,SRIN=srim.PrepSrimFile( ion=incomming0, energy=Eini, angle=0., number=number,
                            mater=material, thick=thick, dens=rho  )
    print('DDD... after PrepSrimFile',Eini, thick)
    sr.get_sr_loss( SRIN , Eini, thick , unit="mg")

    return TRIMIN
############# END OF PREPARE TRIMIN















def mainfunc():
    print("i... function defined in main of nuphy")
    return True


if __name__=="__main__":
    print("i... in main:  nuphy ")
