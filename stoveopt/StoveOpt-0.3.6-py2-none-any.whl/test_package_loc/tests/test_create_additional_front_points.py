# -*- coding: utf-8 -*-
"""
Created on Mon May 20 08:06:20 2019

@author: Lee
"""

# Test for the creation of additional front points
def create_additional_front_points(pt6x, pt7x, pt14x, pt9z, pt15x, pt8z, pt14z, pt9x, pt8x, pt15z):
    """Create pot surface points to create faces--Nameing them 21(L)-22(R) to not collide with current fuel vert numbers"""
    # Left point
    pt20x = pt6x
    pt20z = pt14z
    pt20y = 0
    # Right point
    pt21x = pt7x
    pt21z = pt15z
    pt21y = 0
    
    pt44x = pt14x
    pt44z = pt9z
    pt44y = 0
    
    pt46x = pt15x
    pt46z = pt8z
    pt46y = 0
    
    pt48x = pt9x
    pt48z = pt14z
    pt48y = 0
    
    pt50x =  pt8x
    pt50z = pt15z
    pt50y = 0
    
    return pt48x, pt48z, pt48y, pt20x, pt20z, pt20y, pt21x, pt21z, pt21y, pt44x, pt44z, pt44y, pt46x, pt46z, pt46y, pt50x, pt50z, pt50y


def test_create_additional_front_points():
    pt6x = 4
    pt7x = -1
    pt14x = 0.000000
    pt9z = 100000
    pt8x = 12.656
    pt15z = -100.678
    pt15x = 0.21
    pt8z = 0
    pt14z = 9
    pt9x = 0

    
    pt48x, pt48z, pt48y, pt20x, pt20z, pt20y, pt21x, pt21z, pt21y, pt44x, pt44z, pt44y, pt46x, pt46z, pt46y, pt50x, pt50z, pt50y = create_additional_front_points(pt6x, pt7x, pt14x, pt9z, pt15x, pt8z, pt14z, pt9x, pt8x, pt15z)
    
    assert pt20x == pt6x
    assert pt20z == pt14z
    assert pt20y == 0
    # Right point
    assert pt21x == pt7x
    assert pt21z == pt15z
    assert pt21y == 0
    
    assert pt44x == pt14x
    assert pt44z == pt9z
    assert pt44y == 0
    
    assert pt46x == pt15x
    assert pt46z == pt8z
    assert pt46y == 0
    
    assert pt48x == pt9x
    assert pt48z == pt14z
    assert pt48y == 0
    
    assert pt50x ==  pt8x
    assert pt50z == pt15z
    assert pt50y == 0
    




