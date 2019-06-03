import numpy as np
import math
from instrument.geometry.pml import weave
from instrument.geometry import shapes, operations
import os, sys


class Clampcell(object):

    def __init__(self, total_height=False):

        self.sample_height=28.57 #mm

        if total_height is True:
            self.sample_height=95.758


    ###### OUTER BODY #############
    def outer_body(self):
        Al_OutDiameter = 32.05 # mm
        Al_OutRadius=Al_OutDiameter/2
        Al_Height=self.sample_height #28.57 #mm (total height 95.758 mm)
        Al_InSmallestCone_Dia= 14.59 #mm (inner boundary is tappered cylinder, bottom Diameter )
        Al_InSmallestCone_Rad=Al_InSmallestCone_Dia/2
        Al_InconeAngle= 2

        Al_InHeight=Al_Height+10 #mm (tappered cylinder height) (this should be same as Al_Height, but in constructive geometry the inner height has to be larger for correct subtraction)

        Al_InLargestCone_Dia= (2* np.tan(np.deg2rad(Al_InconeAngle/2))*Al_InHeight)+Al_InSmallestCone_Dia #( tappered cylinder top diameter)
        Al_InLargestCone_Rad=Al_InLargestCone_Dia/2
        Al_InSmallest_ConeHeight=Al_InSmallestCone_Dia/(2*np.tan(np.deg2rad(Al_InconeAngle/2)))
        Al_InLargest_ConeHeight=Al_InSmallest_ConeHeight+Al_InHeight
        Al_boxHeightToSubtract=Al_InSmallest_ConeHeight*2
        Al_boxthisckness= Al_InSmallestCone_Dia+20
        Al_HalfHeight=Al_InHeight/2
        Al_moving_height=Al_InSmallest_ConeHeight+Al_HalfHeight

        ### CReate the string for OUTER BODY ######
        Al_OutRadius_str=str(Al_OutRadius)+r'*mm'
        Al_Height_str=str(Al_Height)+r'*mm'
        Al_InLargestCone_Rad_str=str(Al_InLargestCone_Rad)+r'*mm'
        Al_InLargest_ConeHeight_str=str(Al_InLargest_ConeHeight)+r'*mm'
        Al_InSmallest_ConeHeight_str=str(Al_InSmallest_ConeHeight)+r'*mm'
        Al_boxHeightToSubtract_str=str(Al_boxHeightToSubtract)+r'*mm'
        Al_boxthisckness_str=str(Al_boxthisckness)+r'*mm'
        Al_moving_height_str=str(-Al_moving_height)+r'*mm'


        #create the inner Al largest cone
        Al_largest_cone=shapes.cone(radius=Al_InLargestCone_Rad_str, height=Al_InLargest_ConeHeight_str) # upside down
        #rotation to make top wider
        Al_largest_cone_widertip=operations.rotate(Al_largest_cone, angle="180*deg",vertical="0",transversal="1",beam="0")
        #make a tapered cylinder
        Al_tapered_cylinder= operations.Difference(Al_largest_cone_widertip,
                                                shapes.block(thickness=Al_boxthisckness_str,height=Al_boxHeightToSubtract_str,width=Al_boxthisckness_str) )
        #moving the center of the cylinder to the center of the coordinate
        Al_centered_taperedCylinder=operations.translate(Al_tapered_cylinder, vertical=Al_moving_height_str)

        #Creating the outer Al body
        outer_Al = operations.subtract(
            shapes.cylinder(radius=Al_OutRadius_str, height=Al_Height_str),
            Al_centered_taperedCylinder,
            )
        return(outer_Al)



    ######## INNER SLEEVE ##########
    def inner_sleeve(self):
        CuBe_InDiameter = 4.74 # mm
        CuBe_InRadius=CuBe_InDiameter/2
        CuBe_InHeight=self.sample_height+10 #mm (total height 95.758 mm)
        CuBe_Height=self.sample_height
        CuBe_OutSmallestCone_Dia=14.63 #(outer boundary is tappered cylinder, bottom diameter )
        CuBe_OutSmallestCone_Rad=CuBe_OutSmallestCone_Dia/2
        CuBe_OutconeAngle= 2 # the tappered angle

        CuBe_OutLargestCone_Dia= (2* np.tan(np.deg2rad(CuBe_OutconeAngle/2))*CuBe_Height)+CuBe_OutSmallestCone_Dia #( tappered cylinder top diamter)
        CuBe_OutLargestCone_Rad=CuBe_OutLargestCone_Dia/2
        CuBe_OutSmallest_ConeHeight=CuBe_OutSmallestCone_Dia/(2*np.tan(np.deg2rad(CuBe_OutconeAngle/2)))
        CuBe_OutLargest_ConeHeight=CuBe_OutSmallest_ConeHeight+CuBe_Height
        CuBe_boxHeightToSubtract=CuBe_OutSmallest_ConeHeight*2
        CuBe_boxthisckness= CuBe_OutSmallestCone_Dia+20
        CuBe_HalfHeight=CuBe_Height/2
        CuBe_moving_height=CuBe_OutSmallest_ConeHeight+CuBe_HalfHeight

        ### CReate the string for INNER SLEEVE ######
        CuBe_InRadius_str=str(CuBe_InRadius)+r'*mm'
        CuBe_InHeight_str=str(CuBe_InHeight)+r'*mm'
        CuBe_Height_str=str(CuBe_Height)+r'*mm'
        CuBe_OutLargestCone_Rad_str=str(CuBe_OutLargestCone_Rad)+r'*mm'
        CuBe_OutLargest_ConeHeight_str=str(CuBe_OutLargest_ConeHeight)+r'*mm'
        CuBe_boxHeightToSubtract_str=str(CuBe_boxHeightToSubtract)+r'*mm'
        CuBe_boxthisckness_str=str(CuBe_boxthisckness)+r'*mm'
        CuBe_moving_height_str=str(-CuBe_moving_height)+r'*mm'

        #create the outer CuBe largest cone
        CuBe_largest_cone=shapes.cone(radius=CuBe_OutLargestCone_Rad_str, height=CuBe_OutLargest_ConeHeight_str) # upside down
        #rotation to make top wider
        CuBe_largest_cone_widertip=operations.rotate(CuBe_largest_cone, angle="180*deg",vertical="0",transversal="1",beam="0")
        #make a tapered cylinder
        CuBe_tapered_cylinder= operations.Difference(CuBe_largest_cone_widertip,
                                                shapes.block(thickness=CuBe_boxthisckness_str,height=CuBe_boxHeightToSubtract_str,width=CuBe_boxthisckness_str) )
        #moving the center of the cylinder to the center of the coordinate
        CuBe_centered_taperedCylinder=operations.translate(CuBe_tapered_cylinder, vertical=CuBe_moving_height_str)

        #Creating the InnerSleeve
        CuBe_innerSleeve = operations.subtract(
            CuBe_centered_taperedCylinder,
            shapes.cylinder(radius=CuBe_InRadius_str, height=CuBe_InHeight_str),

            )
        return(CuBe_innerSleeve)





    ####### SAMPLE ######### ( the sample is a cylinder)
    def sample(self):
        sample_Height=27.3 #mm
        sample_Diameter=4.16 #mm
        sample_Radius=sample_Diameter/2

        ##covert to string###
        sample_Height_str=str(sample_Height)+r'*mm'
        sample_Radius_str=str(sample_Radius)+r'*mm'
        ##cylindrical sample##
        sample= shapes.cylinder(radius=sample_Radius_str, height=sample_Height_str)
        return(sample)



