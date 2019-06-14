# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 13:19:12 2019

@author: Lee
"""
import inspect
import os
import xlrd
import numpy
from pathlib import Path

def extract_geometry(file_path):
    """Pulling Data from excel workbook"""
    file_path = Path(file_path)
    
    """singleSlash = "\\" #    WOW THIS IS INCREDIBLE FRUSTRATING--I think the tests folder might need to be capatilized...
    doubleSlash = "\\\\"---THE FILEPATH NEEDS TO BE SINGLE FORWARD SLASHES FOR THE PATH FUNCTION TO WORK
    file_path_geom = file_path.replace(singleSlash,doubleSlash)"""
    
    """ Going to put the conversion functionality in the parse arguments section"""
    
    workbook = xlrd.open_workbook(file_path)
    worksheet = workbook.sheet_by_name('Outputs')
    pt1x = worksheet.cell(1,2).value
    pt1z = worksheet.cell(1,3).value
    pt1y = worksheet.cell(1,4).value
    pt2x = worksheet.cell(2,2).value
    pt2z = worksheet.cell(2,3).value
    pt2y = worksheet.cell(2,4).value
    pt3x = worksheet.cell(3,2).value
    pt3z = worksheet.cell(3,3).value
    pt3y = worksheet.cell(3,4).value
    pt4x = worksheet.cell(4,2).value
    pt4z = worksheet.cell(4,3).value
    pt4y = worksheet.cell(4,4).value
    pt5x = worksheet.cell(5,2).value
    pt5z = worksheet.cell(5,3).value
    pt5y = worksheet.cell(5,4).value
    pt6x = worksheet.cell(6,2).value
    pt6z = worksheet.cell(6,3).value
    pt6y = worksheet.cell(6,4).value
    pt7x = worksheet.cell(7,2).value
    pt7z = worksheet.cell(7,3).value
    pt7y = worksheet.cell(7,4).value
    pt8x = worksheet.cell(8,2).value
    pt8z = worksheet.cell(8,3).value
    pt8y = worksheet.cell(8,4).value
    pt9x = worksheet.cell(9,2).value
    pt9z = worksheet.cell(9,3).value
    pt9y = worksheet.cell(9,4).value
    pt10x = worksheet.cell(10,2).value
    pt10z = worksheet.cell(10,3).value
    pt10y = worksheet.cell(10,4).value
    pt11x = worksheet.cell(11,2).value
    pt11z = worksheet.cell(11,3).value
    pt11y = worksheet.cell(11,4).value
    pt12x = worksheet.cell(12,2).value
    pt12z = worksheet.cell(12,3).value
    pt12y = worksheet.cell(12,4).value
    pt13x = worksheet.cell(13,2).value
    pt13z = worksheet.cell(13,3).value
    pt13y = worksheet.cell(13,4).value
    pt14x = worksheet.cell(14,2).value
    pt14z = worksheet.cell(14,3).value
    pt14y = worksheet.cell(14,4).value
    pt15x = worksheet.cell(15,2).value
    pt15z = worksheet.cell(15,3).value
    pt15y = worksheet.cell(15,4).value
    pt16x = worksheet.cell(16,2).value
    pt16z = worksheet.cell(16,3).value
    pt16y = worksheet.cell(16,4).value
    #U_100x = worksheet.cell(17,2).value
    #U_100z = worksheet.cell(17,3).value # Not really using the other 2-dimensions for now
    #U_100y = worksheet.cell(17,4).value
    
    if pt16z == 0:
        print("Top point has a 0 height value--error in data import")
    return pt1x, pt1z, pt1y, pt2x, pt2z, pt2y, pt3x, pt3z, pt3y, pt4x, pt4z, pt4y, pt5x, pt5z, pt5y, pt6x, pt6z, pt6y, pt7x, pt7z, pt7y, pt8x, pt8z, pt8y, pt9x, pt9z, pt9y, pt10x, pt10z, pt10y, pt11x, pt11z, pt11y, pt12x, pt12z, pt12y, pt13x, pt13z, pt13y,  pt14x, pt14z, pt14y, pt15x, pt15z, pt15y, pt16x, pt16z, pt16y


def test_extract_geometry():
    """ purpose of the test is to test that geometry can be pulled from xlsx (modern) excel versions--comparing returned values to a locked spreadsheet"""
    file_path = 'C:/Oregon_State/Spring_2019/Soft_dev_eng/StoveOpt/tests/Stove_test_Geometry.xlsx'
    pt1x, pt1z, pt1y, pt2x, pt2z, pt2y, pt3x, pt3z, pt3y, pt4x, pt4z, pt4y, pt5x, pt5z, pt5y, pt6x, pt6z, pt6y, pt7x, pt7z, pt7y, pt8x, pt8z, pt8y, pt9x, pt9z, pt9y, pt10x, pt10z, pt10y, pt11x, pt11z, pt11y, pt12x, pt12z, pt12y, pt13x, pt13z, pt13y,  pt14x, pt14z, pt14y, pt15x, pt15z, pt15y, pt16x, pt16z, pt16y = extract_geometry(file_path)
    assert pt2x == 0.1
    assert pt2z == 0
    assert pt2y == 0
    assert pt3x == 0
    assert pt3z == 0.15
    assert pt3y == 0
    assert pt4x == 0.1
    assert pt4z == 0.15
    assert pt4y == 0
    assert pt5x == 0.1
    assert pt5z == 0.16
    assert pt5y == 0
    assert pt6x == 0
    assert pt6z == 0.16
    assert pt6y == 0
    assert pt7x == 0
    assert pt7z == 0.3
    assert pt7y == 0
    assert pt8x == 0.1
    assert pt8z == 0.3
    assert pt8y == 0
    assert pt9x == 0.17
    assert pt9z == 0.3
    assert pt9y == 0
    assert pt10x == -0.07
    assert pt10z == 0.3
    assert pt10y == 0
    assert pt11x == -0.07
    assert pt11z == 0.5
    assert pt11y == 0
    assert pt12x == -.04
    assert pt12z == 0.5
    assert pt12y == 0
    assert pt13x == 0.14
    assert pt13z == 0.5
    assert pt13y == 0
    assert pt14x == 0.17
    assert pt14z == 0.5
    assert pt14y == 0
    assert pt15x == -0.04
    assert pt15z == 0.33
    assert pt15y == 0
    assert pt16x == 0.14
    assert pt16z == 0.33
    assert pt16y == 0
    #assert U_100x == 1
    #assert U_100y == 0
    #assert U_100z == 0
    
    