# -*- coding: utf-8 -*-
"""
Created on Thu May  2 19:22:11 2019

@author: Lee
"""

"""Input two set pt0x and pt1x, assert what the coordinates should be"""

pt0x = 0 # Origin
pt1x = 3 # assigned random

# Create additional front face points including wood zone
def create_fuel_blocks(pt0x, pt1x):
    """Uses the geometric variables computed in assign_geomvars to create zones for the wood fuel zone:
       1) Rectangular fuel source
       2) centered along the flow axis of combustion chamber
       3) Half the width of the bottom of the chamber
       4) Assumed fuel wood height of 3 inches (0.0762 m)
       5) Assumed the bottom of the wood is 3 inches off of the ground (0.0762 m)
       6) pt17 is bottom left, pt18 is bottom right, pt19 is top right, pt20 is top left"""
    fuel_width = 0.5*(pt1x - pt0x)
    print("Fuel width: " + str(fuel_width))
    print("pt0x :" + str(pt0x))
    print("pt1x :" + str(pt1x))
    
    fuel_x_center = fuel_width
    fuel_x_left_coord = fuel_x_center - (fuel_width)/2
    fuel_x_right_coord = fuel_x_center + (fuel_width)/2
    fuel_height = 0.0762 # [m]
    fuel_bottom_coords = 0.0762
    fuel_top_coords = fuel_bottom_coords + fuel_height
    pt16x = fuel_x_left_coord
    pt17x = fuel_x_right_coord
    pt18x = fuel_x_right_coord
    pt19x = fuel_x_left_coord
    pt16z = fuel_bottom_coords
    pt17z = fuel_bottom_coords
    pt18z = fuel_top_coords
    pt19z = fuel_top_coords
    pt16y = 0
    pt17y = 0
    pt18y = 0
    pt19y = 0
    return pt17x, pt18x, pt19x, pt16x, pt17z, pt18z, pt19z, pt16z, pt17y, pt18y, pt19y, pt16y


# Fuel is centered in combustion chamber, half of the width defined by points 0 and 1
def test_create_fuel_blocks():
    """Test the coordinates of the fuel put out by the function"""
    pt0x = 0 # Origin
    pt1x = 3 # assigned random
    pt17x, pt18x, pt19x, pt16x, pt17z, pt18z, pt19z, pt16z, pt17y, pt18y, pt19y, pt16y = create_fuel_blocks(pt0x, pt1x)
    fuel_width = 1.5
    fuel_x_left_coord_expected = 0.75
    fuel_x_right_coord_expected = 2.25
    print("This is pt17x:" + " " +  str(pt17x))
    print("This is pt19x:" + " " +  str(pt19x))
    
    assert pt17x == fuel_x_right_coord_expected
    assert pt19x == fuel_x_left_coord_expected










